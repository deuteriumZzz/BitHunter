import gym
import numpy as np
from gym import spaces
from .models import HistoricalData, Prediction

class TradingEnv(gym.Env):
    def __init__(self, historical_data, news_features, initial_balance=10000):
        super(TradingEnv, self).__init__()
        self.historical_data = historical_data
        self.news_features = news_features
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.current_step = 0
        self.max_steps = len(historical_data) - 1

        self.action_space = spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell
        self.observation_space = spaces.Box(low=0, high=1, shape=(len(historical_data[0]) + len(news_features[0]) + 1,), dtype=np.float32)

    def reset(self):
        self.balance = self.initial_balance
        self.current_step = 0
        return self._get_obs()

    def step(self, action):
        current_price = self.historical_data[self.current_step][0]
        reward = 0

        if action == 1:  # Купить
            self.balance -= current_price * 0.01
        elif action == 2:  # Продать
            self.balance += current_price * 0.01
            reward = 0.1

        self.current_step += 1
        done = self.current_step >= self.max_steps
        obs = self._get_obs()
        return obs, reward, done, {}

    def _get_obs(self):
        hist = np.array(self.historical_data[self.current_step])
        news = np.array(self.news_features[self.current_step])
        balance_norm = self.balance / self.initial_balance
        return np.concatenate([hist, news, [balance_norm]])
