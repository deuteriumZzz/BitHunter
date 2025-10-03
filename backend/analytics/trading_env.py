# analytics/trading_env.py
import gym
import numpy as np
from gym import spaces
from django.core.exceptions import ValidationError
from .models import HistoricalData, Prediction  # Импорт моделей Django для интеграции

class TradingEnv(gym.Env):
    """
    RL-среда для симуляции торговли криптовалютой с использованием исторических данных и sentiment-анализа новостей.
    Фичи:
    - Observation: нормализованные [price, volume, sentiment, balance]
    - Actions: 0=hold, 1=buy (long), 2=sell (short)
    - Reward: реалистичный, учитывает profit/loss, позиции, комиссии
    - Интеграция с Django: опциональное сохранение Prediction в БД
    - Обработка ошибок и нормализация
    """
    
    def __init__(self, historical_data, news_features, initial_balance=10000, user=None):
        super(TradingEnv, self).__init__()
        
        # Преобразование входных данных в numpy массивы для удобства
        self.historical_data = np.array(historical_data)  # Ожидается: [[price, volume], ...]
        self.news_features = np.array(news_features).reshape(-1, 1)  # Ожидается: [[sentiment], ...] или [sentiment, ...]
        
        # Проверки на корректность данных
        if len(self.historical_data) == 0 or len(self.news_features) == 0:
            raise ValidationError("historical_data and news_features cannot be empty")
        if len(self.historical_data) != len(self.news_features):
            raise ValidationError("historical_data and news_features must have the same length")
        if self.historical_data.shape[1] < 2:
            raise ValidationError("historical_data must have at least price and volume columns")
        
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.current_step = 0
        self.max_steps = len(self.historical_data) - 1
        self.position = 0  # 0: no position, 1: long, -1: short
        self.user = user  # Для сохранения Prediction в БД (опционально)
        
        # Action space: 3 действия
        self.action_space = spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell
        
        # Observation space: фиксированный размер [price_norm, volume_norm, sentiment_norm, balance_norm]
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        
        # Вычисление min/max для нормализации (на основе всех данных)
        self.price_min = np.min(self.historical_data[:, 0])
        self.price_max = np.max(self.historical_data[:, 0])
        self.volume_min = np.min(self.historical_data[:, 1])
        self.volume_max = np.max(self.historical_data[:, 1])
        self.sentiment_min = np.min(self.news_features)
        self.sentiment_max = np.max(self.news_features)
        
        # Защита от деления на ноль
        if self.price_max == self.price_min:
            self.price_min -= 1e-6
            self.price_max += 1e-6
        if self.volume_max == self.volume_min:
            self.volume_min -= 1e-6
            self.volume_max += 1e-6
        if self.sentiment_max == self.sentiment_min:
            self.sentiment_min -= 1e-6
            self.sentiment_max += 1e-6

    def reset(self):
        """Сброс среды к начальному состоянию."""
        self.balance = self.initial_balance
        self.current_step = 0
        self.position = 0
        return self._get_obs()

    def step(self, action):
        """
        Выполнить шаг в среде.
        - action: 0=hold, 1=buy, 2=sell
        - Возвращает: obs, reward, done, info
        """
        if self.current_step >= self.max_steps:
            return self._get_obs(), 0, True, {}
        
        current_price = self.historical_data[self.current_step, 0]
        next_price = self.historical_data[self.current_step + 1, 0] if self.current_step + 1 <= self.max_steps else current_price
        commission_rate = 0.001  # 0.1% комиссия
        reward = 0
        
        # Логика действий
        if action == 1 and self.position != 1:  # Buy (enter long)
            cost = current_price * (1 + commission_rate)
            if self.balance >= cost:
                self.balance -= cost
                self.position = 1
        elif action == 2 and self.position != -1:  # Sell (enter short)
            proceeds = current_price * (1 - commission_rate)
            self.balance += proceeds
            self.position = -1
        # Hold: ничего не делаем
        
        # Вычисление reward на основе позиции и изменения цены
        if self.position == 1:  # Long: profit если цена растёт
            reward = (next_price - current_price) / current_price * 100  # Процентная прибыль
        elif self.position == -1:  # Short: profit если цена падает
            reward = (current_price - next_price) / current_price * 100
        
        # Опционально: сохранить Prediction в БД (если user задан)
        if self.user:
            try:
                prediction = Prediction(
                    action=action,
                    predicted_price=next_price,
                    actual_price=next_price,  # Для простоты, можно заменить на реальные данные
                    user=self.user,
                    timestamp=self.historical_data[self.current_step + 1, 0] if self.current_step + 1 <= self.max_steps else None
                )
                prediction.save()
            except Exception as e:
                # Логировать ошибку, но не прерывать симуляцию
                print(f"Error saving Prediction: {e}")
        
        self.current_step += 1
        done = self.current_step >= self.max_steps
        obs = self._get_obs()
        return obs, reward, done, {}

    def _get_obs(self):
        """Получить нормализованное наблюдение."""
        if self.current_step >= len(self.historical_data):
            return np.zeros(4, dtype=np.float32)
        
        price = self.historical_data[self.current_step, 0]
        volume = self.historical_data[self.current_step, 1]
        sentiment = self.news_features[self.current_step, 0]
        balance_norm = self.balance / self.initial_balance
        
        # Нормализация в [0, 1]
        price_norm = (price - self.price_min) / (self.price_max - self.price_min)
        volume_norm = (volume - self.volume_min) / (self.volume_max - self.volume_min)
        sentiment_norm = (sentiment - self.sentiment_min) / (self.sentiment_max - self.sentiment_min)
        
        return np.array([price_norm, volume_norm, sentiment_norm, balance_norm], dtype=np.float32)

    def render(self, mode='human'):
        """Визуализация (опционально, для отладки)."""
        print(f"Step: {self.current_step}, Balance: {self.balance:.2f}, Position: {self.position}, "
              f"Price: {self.historical_data[self.current_step, 0]:.2f}")
