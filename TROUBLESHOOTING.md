# 🔧 Troubleshooting Guide

## Lỗi "ERR_ADDRESS_INVALID" khi truy cập

### Vấn đề
Khi truy cập `http://0.0.0.0:8000/` trong trình duyệt, bạn sẽ gặp lỗi:
```
ERR_ADDRESS_INVALID
This site can't be reached
```

### Nguyên nhân
`0.0.0.0` là địa chỉ để server **listen** trên tất cả interfaces, nhưng **không phải** địa chỉ để truy cập từ trình duyệt.

### Giải pháp

✅ **Sử dụng một trong các địa chỉ sau:**
- `http://localhost:8000`
- `http://127.0.0.1:8000`

### Cách chạy server

```bash
# Chạy server
python run_api.py
```

Server sẽ hiển thị:
```
🚀 Starting VeriModel Server...
📡 Server will be available at:
   - http://localhost:8000
   - http://127.0.0.1:8000
```

Sau đó mở trình duyệt và truy cập: **http://localhost:8000**

## Các lỗi khác

### 1. Port 8000 đã được sử dụng

**Lỗi:** `[Errno 48] Address already in use`

**Giải pháp:**
```bash
# Tìm process đang dùng port 8000
netstat -ano | findstr :8000

# Kill process (thay PID bằng số từ lệnh trên)
taskkill /PID <PID> /F

# Hoặc đổi port
# Sửa port trong run_api.py thành 8001 hoặc port khác
```

### 2. Module không tìm thấy

**Lỗi:** `ModuleNotFoundError: No module named 'xxx'`

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### 3. Static files không load

**Vấn đề:** CSS/JS không hiển thị

**Kiểm tra:**
- Đảm bảo thư mục `static/` tồn tại
- Đảm bảo file `static/app.js` tồn tại
- Kiểm tra console trong browser (F12) xem có lỗi 404 không

### 4. Server không start

**Kiểm tra:**
```bash
# Test import
python -c "from verimodel.api_server import app; print('OK')"

# Test uvicorn
python -c "import uvicorn; print('OK')"
```

## Kiểm tra Server

Sau khi start server, test:

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Hoặc dùng Python
python test_server.py
```

## Logs và Debug

Để xem logs chi tiết:

```bash
# Chạy với debug mode
uvicorn verimodel.api_server:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Windows Specific

Trên Windows, nếu gặp vấn đề với firewall:

1. Cho phép Python qua Windows Firewall
2. Hoặc tắt firewall tạm thời để test

