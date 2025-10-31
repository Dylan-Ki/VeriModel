# HƯỚNG DẪN SỬ DỤNG VERIMODEL

## 1. Cài đặt môi trường
- Yêu cầu Python 3.8+
- Cài đặt các thư viện cần thiết:
  ```bash
  pip install typer rich
  ```

## 2. Chạy chương trình
- Sử dụng lệnh sau để quét file pickle:
  ```bash
  python -m verimodel.cli scan <đường_dẫn_đến_file.pkl>
  ```
- Các tuỳ chọn:
  - `--static-only` hoặc `-s`: Chỉ quét tĩnh (bỏ qua quét động)
  - `--dynamic-only` hoặc `-d`: Chỉ quét động (bỏ qua quét tĩnh)
  - `--verbose` hoặc `-v`: Hiển thị chi tiết kết quả
  - `--timeout` hoặc `-t`: Thời gian timeout cho quét động (giây, mặc định 5)

## 3. Hiển thị thông tin file
- Xem thông tin cơ bản về file pickle:
  ```bash
  python -m verimodel.cli info <đường_dẫn_đến_file.pkl>
  ```

## 4. Kết quả quét
- Kết quả sẽ được hiển thị rõ ràng trên cửa sổ dòng lệnh với các phần:
  - **Header**: Tên chương trình, tên file đang quét
  - **Quét tĩnh**: Phát hiện các opcode nguy hiểm, cảnh báo
  - **Quét động**: Phát hiện hành vi nguy hiểm khi thực thi (chỉ hỗ trợ Linux)
  - **Kết luận tổng thể**: Đánh giá file an toàn hay nguy hiểm
  - **Khuyến nghị**: Đề xuất hành động tiếp theo nếu file nguy hiểm

## 5. Ví dụ sử dụng
```bash
python -m verimodel.cli scan model.pkl --verbose
python -m verimodel.cli scan model.pkl --static-only
python -m verimodel.cli scan model.pkl --dynamic-only --timeout 10
python -m verimodel.cli info model.pkl
```

## 6. Lưu ý
- Quét động chỉ hỗ trợ trên hệ điều hành Linux và yêu cầu cài đặt `strace`.
- Nên sử dụng cả hai chế độ quét để đảm bảo an toàn tối đa.
- Không tải các file được đánh giá là nguy hiểm vào môi trường production.
