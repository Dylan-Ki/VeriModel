# Hướng dẫn Cài đặt VeriModel

VeriModel là một công cụ giúp quét và phân tích các file mô hình AI để phát hiện mã độc.

## Yêu cầu hệ thống
- Python 3.7 trở lên
- Windows/Linux/MacOS

## Cách cài đặt

### 1. Cài đặt Python
- Tải Python từ [python.org](https://www.python.org/downloads/)
- Chọn phiên bản Python 3.7 trở lên
- Trong quá trình cài đặt, nhớ tích vào "Add Python to PATH"

### 2. Tải VeriModel
- Tải file ZIP của project từ GitHub
- Giải nén vào thư mục bạn muốn

### 3. Cài đặt các thư viện cần thiết
Mở Terminal/Command Prompt trong thư mục vừa giải nén và chạy:
```
pip install -r requirements.txt
```

### 4. Khởi động ứng dụng
Từ thư mục đã giải nén, chạy lệnh:
```
python -m verimodel.gui
```

## Cách sử dụng

1. Quét an toàn:
   - Click vào tab "Quét an toàn"
   - Chọn file cần quét (.pkl, .pth)
   - Chọn loại quét (tĩnh/động)
   - Click "Quét ngay"

2. Phân tích chi tiết:
   - Click vào tab "Phân tích chi tiết"
   - Chọn file cần phân tích
   - Click "Phân tích chi tiết"
   - Xem kết quả trong các tab

## Lưu ý an toàn

- Luôn quét file trước khi sử dụng trong production
- Chỉ sử dụng mô hình từ nguồn đáng tin cậy
- Đặc biệt cẩn thận với file Pickle
- Kiểm tra kỹ các cảnh báo bảo mật

## Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.