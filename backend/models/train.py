import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from lstm_model import build_lstm_model

# Load dữ liệu
train_data = pd.read_csv("data/processed/train.csv").values

# Chuẩn hóa dữ liệu
scaler = MinMaxScaler(feature_range=(0, 1))
train_scaled = scaler.fit_transform(train_data)

# Chia dữ liệu
X_train, y_train = train_scaled[:, :-1], train_scaled[:, -1]

# Xây dựng mô hình
model = build_lstm_model((X_train.shape[1], 1))
model.fit(X_train, y_train, epochs=50, batch_size=64)

# Lưu mô hình
model.save("models/lstm_model.h5")
print("✅ Training hoàn tất và mô hình đã được lưu!")
