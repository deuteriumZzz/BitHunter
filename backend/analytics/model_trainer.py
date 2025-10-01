import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
import ccxt

class ModelTrainer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.model_path = os.path.join(self.base_dir, 'models/lstm_model.h5')
        self.scaler_path = os.path.join(self.base_dir, 'models/scaler.npy')

    def load_data_from_csv(self, use_ccxt=True, limit=1000):
        if use_ccxt:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1m', limit=limit)
            closes = np.array([x[4] for x in ohlcv])
            return closes
        return None

    def train_model(self, data, look_back=60, epochs=100):
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i, 0])
            y.append(scaled_data[i, 0])
        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(look_back, 1)),
            LSTM(50),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X, y, epochs=epochs, batch_size=32)
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        model.save(self.model_path)
        np.save(self.scaler_path, [scaler.min_, scaler.scale_])
        return model, scaler

    def predict_price(self, input_data, scaler, model):
        prediction = model.predict(input_data)
        return scaler.inverse_transform(prediction)[0][0]
