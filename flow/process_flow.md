# VeriModel - Luồng xử lý và bề mặt tấn công

Tài liệu này mô tả luồng chạy thời gian thực của ứng dụng VeriModel: dữ liệu
di chuyển qua GUI, trình phân tích tĩnh, trình phân tích động và thành phần
báo cáo như thế nào. Đồng thời nêu bề mặt tấn công (threat surface) và các biện
pháp giảm thiểu đề xuất để giảng viên và người đánh giá có thể hiểu thiết kế.

## Các thành phần

- `verimodel.gui` - Giao diện Tkinter cho phép người dùng chọn file, cấu hình
  tùy chọn quét, hiển thị kết quả và xuất báo cáo.
- `verimodel.file_analyzer` - Thành phần điều phối phân tích ở mức file, thực
  hiện phân tích cấu trúc và phân tích.byte của file pickle.
- `verimodel.static_scanner` - Phân tích tĩnh dựa trên `pickletools` để rà soát
  opcode, áp dụng quy tắc và heuristic.
- `verimodel.dynamic_scanner` - Phân tích động bằng cách thực thi loader script
  và giám sát syscall (dùng `strace` trên Linux) để phát hiện hành vi thời gian
  chạy.
- `verimodel.virtual_scan_dir` - Tiện ích tạo thư mục tạm cách ly để xử lý file
  trong khi quét.
- `demo_models` - Tập mẫu diễn tập và script sinh mẫu an toàn / nguy hiểm có
  tuỳ chọn (chỉ tạo khi người dùng đồng ý rõ ràng) dùng cho kiểm thử và giảng dạy.

## Luồng xử lý tổng quát

1. Người dùng mở GUI và chọn file cần quét.
2. GUI copy file vào `virtual_scan_dir` (thư mục tạm cách ly) để tránh sửa
   đổi file gốc.
3. Nếu chọn "Quét tĩnh":
   - GUI tạo instance `StaticScanner` và gọi `scan_file(target_path)`.
   - `StaticScanner` chạy `pickletools.genops` để thu thập chuỗi opcode,
     tìm các mẫu nguy hiểm (ví dụ GLOBAL/REDUCE kèm tham chiếu module đáng ngờ).
   - Kết quả (threats/warnings/details) trả về cho GUI.
4. Nếu chọn "Quét động" (chỉ trên Linux):
   - GUI tạo instance `DynamicScanner` và gọi `scan(str(target_path))`.
   - `DynamicScanner` ghi một loader script để chạy `pickle.load()` trong một
     process tạm và dùng `strace` để ghi lại syscall.
   - `DynamicScanner` phân tích log `strace` và ánh xạ các syscall đáng ngờ
     (ví dụ: kết nối mạng, execve, xóa file) thành phát hiện.
   - Kết quả trả về cho GUI.
5. `FileAnalyzer` có thể được gọi để thu thập thông tin cấu trúc và entropy
   byte (`analyze_file`). Kết quả bao gồm phiên bản protocol, phân bố opcode,
   entropy và một số heuristic đơn giản để gợi ý nội dung có thể thực thi.
6. GUI tổng hợp kết quả và hiển thị:
   - Các phát hiện được tô sáng trong khu vực output.
   - Tóm tắt theo từng loại quét và một kết luận chung.
   - Popup cảnh báo cho các mối nguy nghiêm trọng và khả năng xuất báo cáo (JSON/HTML).

## Định dạng dữ liệu

- Quét tĩnh trả về dictionary: `{"is_safe": bool, "threats": [...], "warnings": [...], "details": [...]}`
- Quét động trả về dictionary tương tự: `{"is_safe": bool, "threats": [...], "syscalls": [...]}`
- FileAnalyzer trả về `{"file_info": {...}, "structure": {...}, "byte_analysis": {...}}`
- Báo cáo có thể xuất ra JSON/HTML chứa các phát hiện và bằng chứng.

## Bề mặt tấn công và biện pháp giảm thiểu

1. Thực thi pickle không đáng tin (quét động & phân tích)
   - Rủi ro: Unpickle có thể thực thi mã tùy ý. Trình quét động hiện tại
     chạy loader script và giám sát bằng `strace`, nhưng điều này có thể không
     ngăn chặn hoàn toàn các hậu quả có hại.
   - Giải pháp: Thực thi untrusted load trong container (Docker) hoặc sandbox
     chuyên dụng (Firecracker, gVisor) với mạng bị vô hiệu hoá, mount chế độ
     chỉ đọc, giới hạn CPU/memory và profile seccomp chặt chẽ.

2. Copy file cục bộ và thư mục tạm
   - Rủi ro: File copy vào thư mục tạm có thể bị đọc hoặc sửa bởi các process khác.
   - Giải pháp: Sử dụng thư mục tạm an toàn với quyền truy cập phù hợp, và
     nếu có thể, tạo namespace tạm thời (unshare) để cô lập; đảm bảo cleanup
     luôn chạy (`try/finally`).

3. Sai lệch trong quy tắc tĩnh (false positives/negatives)
   - Rủi ro: Heuristic có thể bỏ sót mẫu che dấu hoặc gán nhãn sai file vô hại.
   - Giải pháp: Thêm engine quy tắc với whitelist, allowlist dựa trên nguồn/tin
     cậy và cung cấp bằng chứng cho mỗi khớp. Cho phép cấu hình để giảng viên
     điều chỉnh độ nhạy.

4. Chuỗi cung ứng phụ thuộc
   - Rủi ro: Dùng dependency không cố định có thể mang lỗ hổng.
   - Giải pháp: Pin phiên bản trong `requirements.txt`, chạy `pip-audit`/`safety`
     trong CI và cập nhật định kỳ.

5. CI và ký artifact
   - Rủi ro: Phát hành nhị phân không ký cho phép bị giả mạo.
   - Giải pháp: Dùng CI để tạo bản build có thể tái tạo, ký artifact và đăng lên
     GitHub Releases kèm checksum.

## Sơ đồ tuần tự (dạng text)

User -> GUI: chọn file
GUI -> VirtualScanDir: copy file vào sandbox
GUI -> StaticScanner: scan_file
StaticScanner -> GUI: trả về findings
GUI -> DynamicScanner: (tùy chọn) chạy trong container/strace
DynamicScanner -> GUI: trả về findings
GUI -> FileAnalyzer: analyze_file
FileAnalyzer -> GUI: cấu trúc + phân tích byte
GUI -> User: hiển thị, tô sáng phát hiện + popup cảnh báo
GUI -> Reporter: xuất JSON/HTML

## Các deliverable đề xuất cho demo giảng viên

- `flow/process_flow.md` (tài liệu này) và một ảnh kiến trúc (PNG) xuất từ công cụ vẽ sơ đồ.
- `demo_models/` chứa mẫu an toàn và mẫu nguy hiểm (tùy chọn, chỉ khi được opt-in) cùng `README_demo.md`.
- `docker/` chứa Dockerfile sandbox và script `run_sandbox.sh`.
- `reports/` với ví dụ báo cáo HTML cho cả demo an toàn và nghi ngờ.
- Một slide deck ngắn (~5 slide) và kịch bản demo 10-15 phút cho lab.

## Ghi chú

Tài liệu luồng này giúp người đánh giá và giảng viên nắm nhanh kiến trúc hệ thống,
pipeline quét và các đánh đổi an ninh đã thực hiện. Dự án hiện có prototype cho
cả phân tích tĩnh và động; bước tiếp theo quan trọng để sẵn sàng cho môi trường
production là tăng cường sandbox cho phân tích động và bổ sung test tự động cùng CI
để tạo build có thể tái lập.
