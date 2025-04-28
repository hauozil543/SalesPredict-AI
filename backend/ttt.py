import pickle
import numpy as np

# Tải scaler
with open('utils/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Kiểm tra thông số của scaler
print("Số cột mà scaler kỳ vọng:", scaler.n_features_in_)
print("Min của từng cột:", scaler.data_min_)
print("Max của từng cột:", scaler.data_max_)

# Thử giải chuẩn hóa một giá trị
dummy_input = np.zeros((1, scaler.n_features_in_))
dummy_input[0, 0] = 0.541471152799204  # Giá trị dự báo lớn nhất
unscaled = scaler.inverse_transform(dummy_input)[0][0]
print("Giá trị giải chuẩn hóa:", unscaled)