import os

import ccxt
import numpy as np
import pandas as pd  # Добавлено для предобработки больших данных
import tensorflow as tf  # Для GPU-проверки
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential


class ModelTrainer:
    """
    Класс для обучения и использования модели LSTM для предсказания цен.
    """

    def __init__(self, base_dir):
        """
        Инициализирует объект ModelTrainer с базовой директорией.

        :param base_dir: Путь к базовой директории для сохранения моделей.
        """
        self.base_dir = base_dir
        self.model_path = os.path.join(self.base_dir, "models/lstm_model.h5")
        self.scaler_path = os.path.join(self.base_dir, "models/scaler.npy")

    def load_data_from_csv(self, use_ccxt=True, limit=1000):
        """
        Загружает данные о ценах закрытия из API биржи (ccxt) или другого источника.

        :param use_ccxt: Флаг использования ccxt для загрузки данных.
        :param limit: Количество записей для загрузки.
        :return: Массив цен закрытия или None.
        """
        if use_ccxt:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv("BTC/USDT", "1m", limit=limit)
            # Вместо сырых циклов: используем pandas для быстрой обработки (векторизировано)
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            closes = df["close"].values  # Быстрее для больших limit (10k+)
            return closes
        return None

    def train_model(self, data, look_back=60, epochs=100, batch_size=32):
        """
        Обучает модель LSTM на предоставленных данных.

        :param data: Массив данных для обучения.
        :param look_back: Количество предыдущих шагов для предсказания.
        :param epochs: Количество эпох обучения (уменьшено до 100 по умолчанию для тестов).
        :param batch_size: Размер батча (добавлено для гибкости).
        :return: Кортеж из обученной модели и скейлера.
        """
        # GPU-проверка: TensorFlow автоматически использует GPU, если CUDA доступна
        gpus = tf.config.list_physical_devices("GPU")
        if gpus:
            print(f"GPU доступен: {len(gpus)} устройство(а). Обучение будет на GPU.")
        else:
            print("GPU не найден. Обучение на CPU (может быть медленнее).")

        # Предобработка с pandas (вместо сырых циклов for i in range — векторизировано)
        df = pd.DataFrame(data, columns=["close"])
        # Нормализация
        scaler = MinMaxScaler()
        df["scaled_close"] = scaler.fit_transform(df[["close"]])
        # Создание X/y векторизированно (shift и rolling — в 10–50 раз быстрее для больших данных)
        df["y"] = df["scaled_close"].shift(-1)  # Следующая цена как target
        df.dropna(inplace=True)
        # Rolling windows для X (look_back шагов)
        for i in range(1, look_back + 1):
            df[f"lag_{i}"] = df["scaled_close"].shift(i)
        df.dropna(inplace=True)
        # Сбор X и y
        X = df[[f"lag_{i}" for i in range(1, look_back + 1)]].values
        y = df["y"].values
        X = X.reshape(X.shape[0], look_back, 1)  # Для LSTM

        # Пример дополнительных индикаторов для "больших данных" (pandas rolling — адаптируй под нужды)
        df["ma_20"] = df["close"].rolling(window=20).mean()  # Moving Average
        df["rsi"] = self._calculate_rsi(df["close"])  # RSI
        # Если хочешь добавить в модель: X = np.concatenate([X, df[['ma_20', 'rsi']].fillna(0).values.reshape(-1, 2, 1)], axis=1)

        model = Sequential(
            [
                LSTM(50, return_sequences=True, input_shape=(look_back, 1)),
                LSTM(50),
                Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        model.save(self.model_path)
        np.save(self.scaler_path, [scaler.min_, scaler.scale_])
        return model, scaler

    def _calculate_rsi(self, series, period=14):
        """
        Простой расчёт RSI с pandas для больших данных (rolling mean).
        """
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def predict_price(self, input_data, scaler, model):
        """
        Предсказывает цену на основе входных данных с использованием модели и скейлера.

        :param input_data: Подготовленные входные данные для предсказания.
        :param scaler: Скейлер для обратного преобразования.
        :param model: Обученная модель.
        :return: Предсказанная цена.
        """
        prediction = model.predict(input_data)
        return scaler.inverse_transform(prediction)[0][0]
