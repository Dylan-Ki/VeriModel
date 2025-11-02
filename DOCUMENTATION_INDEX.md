# 📚 VeriModel Documentation Index

## Tài liệu chính

### 🏠 [README.md](README.md)
**File chính** - Tổng quan về dự án, cài đặt, và sử dụng cơ bản.

Bao gồm:
- Giới thiệu về VeriModel
- Hướng dẫn cài đặt
- Hướng dẫn sử dụng CLI và Web Interface
- Kiến trúc dự án

### 🌐 [README_WEB.md](README_WEB.md)
**Hướng dẫn Web Interface** - Chi tiết về giao diện web FastAPI.

Bao gồm:
- Cách chạy web interface
- Các tính năng của web UI
- API endpoints
- Cấu trúc files

### 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**Xử lý sự cố** - Hướng dẫn fix các lỗi thường gặp.

Bao gồm:
- Lỗi ERR_ADDRESS_INVALID
- Port đã được sử dụng
- Module không tìm thấy
- Static files không load

### 🐛 [BUGFIXES.md](BUGFIXES.md)
**Log bug fixes** - Ghi chú về các lỗi đã được sửa.

## Tài liệu trong thư mục con

### 📁 demo_models/README_demo.md
Hướng dẫn về các file demo và cách tạo chúng.

### 📁 test_models/README.md
Hướng dẫn về test models.

## Scripts và Tools

### 🚀 run_api.py
Script để chạy FastAPI server.

### 📦 install_dependencies.py
Script tự động cài đặt dependencies.

### 🧪 test_server.py
Script để test các API endpoints.

## Lưu ý

- **KHÔNG** sử dụng `http://0.0.0.0:8000` trong trình duyệt - dùng `http://localhost:8000`
- Web interface **KHÔNG** dùng Streamlit - đã chuyển sang FastAPI + HTML/JavaScript
- Xem [TROUBLESHOOTING.md](TROUBLESHOOTING.md) nếu gặp vấn đề

