# Test Models cho VeriModel

Thư mục này chứa các mô hình pickle để test chương trình VeriModel:

## 1. Mô hình an toàn (safe_model.pkl)
- File: `safe_model.pkl`
- Nội dung: Một danh sách số [1, 2, 3, 4, 5]
- Mục đích: Test phát hiện file an toàn không có mã độc
- Tạo bởi: `create_safe.py`

## 2. Mô hình độc hại (malicious_model.pkl)
- File: `malicious_model.pkl`
- Nội dung: Một object cố gắng thực thi lệnh hệ thống thông qua `os.system`
- Mục đích: Test phát hiện mã độc và cách ly thực thi
- Tạo bởi: `create_malicious.py`

## Cách sử dụng
1. Đảm bảo bạn đang trong thư mục gốc của VeriModel
2. Chạy VeriModel GUI:
   ```bash
   python -m verimodel.gui
   ```
3. Chọn một trong các file test để quét
4. So sánh kết quả với mô tả ở trên

## Lưu ý an toàn
- File `malicious_model.pkl` chứa mã độc minh họa, chỉ dùng cho mục đích test
- KHÔNG tải file này vào môi trường production
- VeriModel sẽ tự động cách ly và quét an toàn trong thư mục tạm