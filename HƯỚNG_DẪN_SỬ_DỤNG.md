
# HƯỚNG DẪN SỬ DỤNG VERIMODEL

## 1. Cài đặt môi trường
- Yêu cầu Python 3.8+
- Cài đặt các thư viện cần thiết:
  ```bash
  pip install typer rich tk
  ```

## 2. Sử dụng giao diện cửa sổ (GUI)
- Chạy giao diện bằng lệnh:
  ```bash
  python -m verimodel.gui
  ```
- Giao diện sẽ cho phép bạn:
  - Chọn file pickle để quét bằng cửa sổ chọn file
  - Chọn chế độ quét tĩnh, quét động hoặc cả hai
  - Nhấn "Quét ngay" để thực hiện quét
- File sẽ được tự động copy vào thư mục tạm trước khi quét để đảm bảo an toàn dữ liệu gốc
- Kết quả hiển thị trực quan, rõ ràng trên cửa sổ với các phần: Quét tĩnh, Quét động, Kết luận tổng thể

## 3. Sử dụng dòng lệnh (CLI)
- Quét file pickle:
  ```bash
  python -m verimodel.cli scan <đường_dẫn_đến_file.pkl>
  ```
- Các tuỳ chọn:
  - `--static-only` hoặc `-s`: Chỉ quét tĩnh (bỏ qua quét động)
  - `--dynamic-only` hoặc `-d`: Chỉ quét động (bỏ qua quét tĩnh)
  - `--verbose` hoặc `-v`: Hiển thị chi tiết kết quả
  - `--timeout` hoặc `-t`: Thời gian timeout cho quét động (giây, mặc định 5)

## 4. Hiển thị thông tin file
- Xem thông tin cơ bản về file pickle:
  ```bash
  python -m verimodel.cli info <đường_dẫn_đến_file.pkl>
  ```

## 5. Kết quả quét
- Kết quả sẽ được hiển thị rõ ràng trên cửa sổ dòng lệnh hoặc giao diện với các phần:
  - **Header**: Tên chương trình, tên file đang quét
  - **Quét tĩnh**: Phát hiện các opcode nguy hiểm, cảnh báo
  - **Quét động**: Phát hiện hành vi nguy hiểm khi thực thi (chỉ hỗ trợ Linux)
  - **Kết luận tổng thể**: Đánh giá file an toàn hay nguy hiểm
  - **Khuyến nghị**: Đề xuất hành động tiếp theo nếu file nguy hiểm

## 6. Ví dụ sử dụng
```bash
python -m verimodel.gui
python -m verimodel.cli scan model.pkl --verbose
python -m verimodel.cli scan model.pkl --static-only
python -m verimodel.cli scan model.pkl --dynamic-only --timeout 10
python -m verimodel.cli info model.pkl
```

## 7. Lưu ý an toàn
- Quét động chỉ hỗ trợ trên hệ điều hành Linux và yêu cầu cài đặt `strace`.
- Nên sử dụng cả hai chế độ quét để đảm bảo an toàn tối đa.
- File sẽ được copy vào thư mục tạm trước khi quét để tránh mất dữ liệu gốc hoặc lỡ thực thi mã độc.
- Không tải các file được đánh giá là nguy hiểm vào môi trường production.
