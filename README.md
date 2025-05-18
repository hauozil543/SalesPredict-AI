# 🧠 M5 Retail Sales Forecasting with LSTM

> **Dự án dự báo doanh số bán lẻ sử dụng mô hình LSTM trên bộ dữ liệu M5 Kaggle.**  
> Ứng dụng gồm backend Flask, frontend React, tích hợp mô hình học sâu PyTorch.

---

## 📁 Cấu trúc thư mục

```
M5/
├── backend/         # Flask backend
│   ├── app.py           # Entry point
│   ├── models/          # Định nghĩa mô hình LSTM
│   ├── routes/          # API routes
│   ├── database/        # Kết nối SQLite/PostgreSQL
│   ├── services/        # Business logic & dự báo
│   ├── static/          # Static files
│   └── utils/           # Hàm tiện ích
│
├── frontend/        # React frontend (Node.js)
│   └── src/             # Source code giao diện
│
├── data/            # Dữ liệu gốc & xử lý
├── notebooks/       # Jupyter notebooks (EDA, thử nghiệm)
├── lstm_model.pth   # File mô hình đã huấn luyện (PyTorch)
├── requirements.txt # Thư viện cần thiết
└── README.md        # File giới thiệu dự án
```

---

## 🔧 Kỹ thuật sử dụng

- **Ngôn ngữ:** Python, JavaScript (React)
- **Backend:** Flask 3.0.3
- **Machine Learning:** PyTorch, scikit-learn
- **Database:** SQLite, PostgreSQL (psycopg2)
- **Frontend:** React (Node.js)
- **Mô hình chính:** LSTM (dự báo chuỗi thời gian)

---

## ⚙️ Hướng dẫn cài đặt & chạy thử

> **Lưu ý:** Thực hiện từng bước theo thứ tự để đảm bảo môi trường hoạt động đúng.

### 1️⃣ Clone dự án

```bash
git clone https://github.com/hauozil543/SalesPredict-AI.git
cd m5
```

### 2️⃣ Thiết lập môi trường ảo

- **Linux/macOS:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
- **Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

### 3️⃣ Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4️⃣ Chạy backend Flask

```bash
cd backend
python app.py
```

### 5️⃣ Chạy frontend React

```bash
cd frontend
npm install
npm run dev
```

---

## 📝 Ghi chú

- **Dữ liệu:** Đặt file dữ liệu gốc vào thư mục `data/` trước khi huấn luyện.
- **Huấn luyện mô hình:** Thực hiện trong notebook data_preparation.ipynb và model_training.ipynb
- **Liên hệ:** hauho3001@gmail.com nếu cần hỗ trợ.

---

> © 2024 - M5 LSTM Retail Forecasting  
> Made with ❤️ by [Jurrien]