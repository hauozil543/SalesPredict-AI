import json
import os

# Dữ liệu đầu vào
data = {
    "X_num": [
        [0.1, 0, 0, 0, 0.05, 0.03, 0.02, 1, 0, 0, 0, 0, 0] + [0] * 26  # Thêm 26 số 0 để đủ 39 đặc trưng
        for _ in range(28)
    ],
    "X_item": [0 for _ in range(28)],
    "X_store": [0 for _ in range(28)]
}

# Đảm bảo thư mục data/ tồn tại
if not os.path.exists('data'):
    os.makedirs('data')

# Lưu dữ liệu vào tệp JSON
with open('data/predict_input.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Tệp JSON đã được tạo tại: data/predict_input.json")