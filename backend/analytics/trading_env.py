"""
Модуль, реализующий среду для обучения с подкреплением (RL) на основе Gym.
Среда симулирует торговлю криптовалютой с использованием исторических данных
и анализа настроений новостей.

Улучшения:
- Награда: Добавлены штрафы за hold в убыточных позициях, бонусы за правильные действия, и компонент риска (на основе drawdown).
- Наблюдения: Включены дополнительные фичи (SMA5, SMA10, RSI) для richer context.
- Backtesting: Добавлен метод backtest() для симуляции и анализа производительности, включая Sharpe ratio и VaR.
- Стоп-лосс/тейк-профит: Автоматические выходы из позиций при достижении уровней.
- Логирование: Добавлено для отладки и мониторинга.
"""

import logging

import gym
import numpy as np
from django.core.exceptions import ValidationError
from gym import spaces

from .models import Prediction

logger = logging.getLogger(__name__)


class TradingEnv(gym.Env):
    """
    RL-среда для симуляции торговли криптовалютой с использованием
    исторических данных и sentiment-анализа новостей.

    Фичи:
    - Observation: нормализованные [price, volume, sentiment, balance, sma5, sma10, rsi]
    - Actions: 0=hold, 1=buy (long), 2=sell (short)
    - Reward: реалистичный, учитывает profit/loss, позиции, комиссии, штрафы и риск
    - Интеграция с Django: опциональное сохранение Prediction в БД
    - Обработка ошибок и нормализация
    - Улучшения: штрафы за hold, дополнительные фичи, backtesting, стоп-лосс/тейк-профит, логирование
    """

    def __init__(
        self,
        historical_data,
        news_features,
        initial_balance=10000,
        user=None,
        stop_loss=0.05,  # 5% убыток для выхода
        take_profit=0.10,  # 10% прибыль для выхода
        hold_penalty=0.1,  # Штраф за hold в убыточной позиции
    ):
        """
        Инициализация среды.

        :param historical_data: Список исторических данных [[price, volume], ...]
        :param news_features: Список sentiment-значений [[sentiment], ...]
        :param initial_balance: Начальный баланс
        :param user: Пользователь для сохранения в БД (опционально)
        :param stop_loss: Процент для стоп-лосс (например, 0.05 = 5%)
        :param take_profit: Процент для тейк-профит (например, 0.10 = 10%)
        :param hold_penalty: Штраф за hold в убыточной позиции
        """
        super(TradingEnv, self).__init__()

        self.historical_data = np.array(historical_data)
        self.news_features = np.array(news_features).reshape(-1, 1)

        if len(self.historical_data) == 0 or len(self.news_features) == 0:
            raise ValidationError("historical_data and news_features cannot be empty")
        if len(self.historical_data) != len(self.news_features):
            raise ValidationError(
                "historical_data and news_features must have the same length"
            )
        if self.historical_data.shape[1] < 2:
            raise ValidationError(
                "historical_data must have at least price and volume columns"
            )

        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.current_step = 0
        self.max_steps = len(self.historical_data) - 1
        self.position = 0  # 0=no position, 1=long, -1=short
        self.entry_price = None  # Цена входа в позицию
        self.user = user
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.hold_penalty = hold_penalty
        self.total_reward = 0  # Для backtesting
        self.portfolio_values = []  # Для трекинга значений портфеля (для метрик)

        self.action_space = spaces.Discrete(3)

        # Обновлено: 7 фич (price, volume, sentiment, balance, sma5, sma10, rsi)
        self.observation_space = spaces.Box(low=0, high=1, shape=(7,), dtype=np.float32)

        # Нормализация для price, volume, sentiment
        self.price_min = np.min(self.historical_data[:, 0])
        self.price_max = np.max(self.historical_data[:, 0])
        self.volume_min = np.min(self.historical_data[:, 1])
        self.volume_max = np.max(self.historical_data[:, 1])
        self.sentiment_min = np.min(self.news_features)
        self.sentiment_max = np.max(self.news_features)

        # Предварительный расчёт SMA и RSI
        self._precompute_features()

        # Нормализация для новых фич
        self.sma5_min = np.min(self.sma5)
        self.sma5_max = np.max(self.sma5)
        self.sma10_min = np.min(self.sma10)
        self.sma10_max = np.max(self.sma10)
        self.rsi_min = 0  # RSI от 0 до 100
        self.rsi_max = 100

        # Коррекция для избежания деления на ноль
        for attr in ["price", "volume", "sentiment", "sma5", "sma10", "rsi"]:
            min_attr = getattr(self, f"{attr}_min")
            max_attr = getattr(self, f"{attr}_max")
            if max_attr == min_attr:
                setattr(self, f"{attr}_min", min_attr - 1e-6)
                setattr(self, f"{attr}_max", max_attr + 1e-6)

    def _precompute_features(self):
        """Предварительный расчёт SMA и RSI для всех шагов."""
        prices = self.historical_data[:, 0]
        self.sma5 = np.convolve(prices, np.ones(5) / 5, mode="valid")
        self.sma5 = np.concatenate(
            [np.full(4, prices[0]), self.sma5]
        )  # Паддинг для первых шагов
        self.sma10 = np.convolve(prices, np.ones(10) / 10, mode="valid")
        self.sma10 = np.concatenate([np.full(9, prices[0]), self.sma10])

        # RSI (простая реализация)
        self.rsi = np.zeros(len(prices))
        for i in range(14, len(prices)):
            gains = np.diff(prices[i - 14 : i + 1])
            avg_gain = np.mean(gains[gains > 0]) if np.any(gains > 0) else 0
            avg_loss = -np.mean(gains[gains < 0]) if np.any(gains < 0) else 0
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            self.rsi[i] = 100 - (100 / (1 + rs))
        # Паддинг для первых 14
        self.rsi[:14] = 50  # Нейтральное значение

    def reset(self):
        """
        Сброс среды к начальному состоянию.

        :return: Начальное наблюдение
        """
        self.balance = self.initial_balance
        self.current_step = 0
        self.position = 0
        self.entry_price = None
        self.total_reward = 0
        self.portfolio_values = [self.initial_balance]  # Сброс трекинга
        return self._get_obs()

    def step(self, action):
        """
        Выполнить шаг в среде.

        :param action: Действие (0=hold, 1=buy, 2=sell)
        :return: Кортеж (obs, reward, done, info)
        """
        if self.current_step >= self.max_steps:
            return self._get_obs(), 0, True, {}

        current_price = self.historical_data[self.current_step, 0]
        next_price = (
            self.historical_data[self.current_step + 1, 0]
            if self.current_step + 1 <= self.max_steps
            else current_price
        )
        commission_rate = 0.001
        reward = 0

        # Проверка стоп-лосс/тейк-профит перед действием
        if self.position != 0 and self.entry_price is not None:
            pnl = (
                (current_price - self.entry_price) / self.entry_price
                if self.position == 1
                else (self.entry_price - current_price) / self.entry_price
            )
            if pnl <= -self.stop_loss or pnl >= self.take_profit:
                # Автоматический выход из позиции
                if self.position == 1:
                    proceeds = current_price * (1 - commission_rate)
                    self.balance += proceeds
                elif self.position == -1:
                    cost = current_price * (1 + commission_rate)
                    self.balance -= cost
                self.position = 0
                self.entry_price = None
                reward += pnl * 100  # Награда за выход

        # Выполнение действия
        if action == 1 and self.position != 1:
            cost = current_price * (1 + commission_rate)
            if self.balance >= cost:
                self.balance -= cost
                self.position = 1
                self.entry_price = current_price
        elif action == 2 and self.position != -1:
            proceeds = current_price * (1 - commission_rate)
            self.balance += proceeds
            self.position = -1
            self.entry_price = current_price

        # Расчёт награды
        if self.position == 1:
            reward += (next_price - current_price) / current_price * 100
        elif self.position == -1:
            reward += (current_price - next_price) / current_price * 100

        # Штраф за hold в убыточной позиции
        if action == 0 and self.position != 0 and self.entry_price is not None:
            pnl = (
                (current_price - self.entry_price) / self.entry_price
                if self.position == 1
                else (self.entry_price - current_price) / self.entry_price
            )
            if pnl < 0:
                reward -= self.hold_penalty

        # Компонент риска: штраф за drawdown (упрощённо, на основе текущего баланса)
        risk_penalty = max(
            0, (self.initial_balance - self.balance) / self.initial_balance * 10
        )
        reward -= risk_penalty

        self.total_reward += reward
        self.portfolio_values.append(self.balance)  # Трекинг значений портфеля

        # Сохранение в БД
        if self.user:
            try:
                prediction = Prediction(
                    action=action,
                    predicted_price=next_price,
                    user=self.user,
                    timestamp=(
                        self.historical_data[self.current_step + 1, 0]
                        if self.current_step + 1 <= self.max_steps
                        else None
                    ),
                )
                prediction.save()
            except Exception as e:
                logger.error(f"Error saving Prediction: {e}")

        self.current_step += 1
        done = self.current_step >= self.max_steps
        obs = self._get_obs()

        logger.debug(
            f"Action taken: {action}, Reward: {reward}, Balance: {self.balance}"
        )
        return obs, reward, done, {}

    def _get_obs(self):
        """
        Получить нормализованное наблюдение.

        :return: Массив нормализованных значений
        """
        if self.current_step >= len(self.historical_data):
            return np.zeros(7, dtype=np.float32)

        price = self.historical_data[self.current_step, 0]
        volume = self.historical_data[self.current_step, 1]
        sentiment = self.news_features[self.current_step, 0]
        balance_norm = self.balance / self.initial_balance
        sma5 = self.sma5[self.current_step]
        sma10 = self.sma10[self.current_step]
        rsi = self.rsi[self.current_step]

        price_norm = (price - self.price_min) / (self.price_max - self.price_min)
        volume_norm = (volume - self.volume_min) / (self.volume_max - self.volume_min)
        sentiment_norm = (sentiment - self.sentiment_min) / (
            self.sentiment_max - self.sentiment_min
        )
        sma5_norm = (sma5 - self.sma5_min) / (self.sma5_max - self.sma5_min)
        sma10_norm = (sma10 - self.sma10_min) / (self.sma10_max - self.sma10_min)
        rsi_norm = (rsi - self.rsi_min) / (self.rsi_max - self.rsi_min)

        return np.array(
            [
                price_norm,
                volume_norm,
                sentiment_norm,
                balance_norm,
                sma5_norm,
                sma10_norm,
                rsi_norm,
            ],
            dtype=np.float32,
        )

    def render(self, mode="human"):
        """
        Визуализация состояния среды (для отладки).

        :param mode: Режим визуализации
        """
        print(
            f"Step: {self.current_step}, Balance: {self.balance:.2f}, "
            f"Position: {self.position}, "
            f"Price: {self.historical_data[self.current_step, 0]:.2f}, "
            f"Entry Price: {self.entry_price if self.entry_price else 'None'}, "
            f"Total Reward: {self.total_reward:.2f}"
        )

    def backtest(self, actions=None):
        """
        Метод для backtesting: симулирует среду с заданными действиями или случайными.
        Возвращает статистику производительности, включая Sharpe ratio и VaR.

        :param actions: Список действий (опционально, иначе случайные)
        :return: Словарь с метриками (total_reward, win_rate, max_drawdown, sharpe_ratio, var_95, etc.)
        """
        self.reset()
        rewards = []
        wins = 0
        losses = 0
        peak_balance = self.balance
        max_drawdown = 0

        for step in range(self.max_steps):
            if actions:
                action = actions[step] if step < len(actions) else 0
            else:
                action = self.action_space.sample()
            obs, reward, done, info = self.step(action)
            rewards.append(reward)
            if reward > 0:
                wins += 1
            elif reward < 0:
                losses += 1
            # Drawdown
            if self.balance > peak_balance:
                peak_balance = self.balance
            drawdown = (peak_balance - self.balance) / peak_balance
            max_drawdown = max(max_drawdown, drawdown)
            if done:
                break

        total_reward = sum(rewards)
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0

        # Расчёт Sharpe ratio и VaR на основе portfolio_values
        if len(self.portfolio_values) > 1:
            returns = np.diff(self.portfolio_values) / np.array(
                self.portfolio_values[:-1]
            )
            sharpe_ratio = (
                np.mean(returns) / np.std(returns) * np.sqrt(252)
                if np.std(returns) > 0
                else 0
            )  # Годовой Sharpe
            var_95 = np.percentile(returns, 5)  # VaR 95% (нижний 5-й процентиль)
        else:
            sharpe_ratio = 0
            var_95 = 0

        logger.info(
            f"Backtest results: Total reward {total_reward}, Sharpe {sharpe_ratio:.2f}, VaR 95% {var_95:.4f}"
        )

        return {
            "total_reward": total_reward,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "final_balance": self.balance,
            "num_trades": wins + losses,
            "sharpe_ratio": sharpe_ratio,
            "var_95": var_95,
        }
