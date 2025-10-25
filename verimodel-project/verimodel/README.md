# 🛡️ VeriModel (AI Supply Chain Firewall)

**VeriModel** là một công cụ bảo mật Giao diện Dòng lệnh (CLI) hoạt động như một "tường lửa" 🧱. Nó cho phép các nhà phát triển và kỹ sư AI/ML quét các tệp mô hình (như `.pkl`, `.pth`) để phát hiện mã độc *trước khi* tải chúng vào môi trường làm việc.

## 1\. 🚨 Vấn đề (The Problem)

Ngành công nghiệp AI/ML đang bùng nổ, và các nhà phát triển thường xuyên tải về các mô hình huấn luyện sẵn từ các nguồn mở như Hugging Face hay GitHub.

  * Phần lớn các mô hình này được lưu trữ dưới định dạng `pickle` của Python (`.pkl`, `.pth`).
  * Định dạng `pickle` vốn dĩ **không an toàn**.
  * Việc `pickle.load()` một tệp từ nguồn không tin cậy có thể dẫn đến lỗ hổng **Thực thi Mã Từ xa (RCE)** 👾, cho phép kẻ tấn công chiếm toàn quyền kiểm soát máy chủ của bạn.
  * Đây là một "lỗ hổng mù" (blind spot) khổng lồ trong chuỗi cung ứng phần mềm AI.

## 2\. 💡 Giải pháp (The Solution)

VeriModel quét các tệp mô hình đáng ngờ bằng cách sử dụng hai cấp độ phân tích:

1.  **🔬 Quét Tĩnh (Static Analysis):** Phân tích an toàn bytecode của tệp `pickle` mà không thực thi nó. Công cụ tìm kiếm các opcode và các hàm `import` nguy hiểm (ví dụ: `os.system`, `subprocess.run`) có thể chỉ ra ý đồ RCE.
2.  \*\* sandbox (Dynamic Analysis):\*\* Thực thi (tải) mô hình một cách an toàn trong một môi trường sandbox bị cô lập (chỉ trên Linux). Công cụ sử dụng `strace` để giám sát chặt chẽ các hành vi độc hại như gọi mạng, thực thi lệnh con, hoặc truy cập tệp hệ thống.

## 3\. 🎬 Demo (Cách hoạt động)

VeriModel được thiết kế để đưa ra cảnh báo rõ ràng khi phát hiện mối đe dọa.

*(Lưu ý: Bạn nên thay thế khối mã bên dưới bằng một video demo `asciinema` như đã đề cập trong tài liệu)*

```sh
$ # 1. Quét một model an toàn
$ verimodel scan demo_models/good_model.pkl
🔍 Đang quét file: good_model.pkl

╭────────────────── Kết quả Quét VeriModel ──────────────────────────────────────────────╮
│ Loại Quét                 │ Trạng thái   │                 Phát hiện                   │
├───────────────────────────┼──────────────┼─────────────────────────────────────────────┤
│ Quét Tĩnh (Pickletools)   │ ✅ An toàn   │    Không tìm thấy opcode nguy hiểm.         │
│ Quét Động (strace/Linux)  │ ✅ An toàn   │ Không phát hiện hành vi hệ thống đáng ngờ.  │
╰────────────────────────────────────────────────────────────────────────────────────────╯

[bold green]✅ An toàn: Không phát hiện mối đe dọa nào. File có vẻ an toàn để tải.[/bold green]

$ # 2. Quét một model chứa mã RCE
$ verimodel scan demo_models/malicious_rce_model.pkl
🔍 Đang quét file: malicious_rce_model.pkl

╭────────────────── Kết quả Quét VeriModel ───────────────────────────────────────────────────╮
│ Loại Quét                 │ Trạng thái    │ Phát hiện                                       │
├───────────────────────────┼───────────────┼─────────────────────────────────────────────────┤
│ Quét Tĩnh (Pickletools)   │ ❌ NGUY HIỂM  │ • Phát hiện GLOBAL opcode nguy hiểm: os.system  │
│ Quét Động (strace/Linux)  │ ❌ NGUY HIỂM  │ • Phát hiện syscall thực thi lệnh (execve)!     │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯

[bold red]⚠️ CẢNH BÁO: Đã phát hiện mối đe dọa tiềm ẩn. KHÔNG tải file này.[/bold red]

$ # 3. Quét một model cố gắng kết nối mạng
$ verimodel scan demo_models/malicious_network_model.pkl
🔍 Đang quét file: malicious_network_model.pkl

╭────────────────── Kết quả Quét VeriModel ──────────────────────────────────────────────────────╮
│ Loại Quét                 │ Trạng thái    │ Phát hiện                                          │
├───────────────────────────┼───────────────┼────────────────────────────────────────────────────┤
│ Quét Tĩnh (Pickletools)   │ ❌ NGUY HIỂM  │ • Phát hiện GLOBAL opcode nguy hiểm: socket.socket │
│ Quét Động (strace/Linux)  │ ❌ NGUY HIỂM  │ • Phát hiện syscall gọi mạng (connect)!            │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯

[bold red]⚠️ CẢNH BÁO: Đã phát hiện mối đe dọa tiềm ẩn. KHÔNG tải file này.[/bold red]
```

## 4\. 🚀 Cài đặt (Installation)

Dự án này sử dụng [Poetry](https://python-poetry.org/) để quản lý các thư viện.

```bash
# 1. Clone repository
git clone https://github.com/your-username/verimodel.git
cd verimodel

# 2. Cài đặt các thư viện (dùng Poetry)
poetry install

# 3. Kích hoạt môi trường ảo
poetry shell

# 4. (Tùy chọn) Tạo các model độc hại để demo
poetry run python generate_malicious_models.py
```

## 5\. 💻 Sử dụng (Usage)

Sau khi cài đặt, bạn có thể chạy lệnh `scan` trên bất kỳ tệp nào.

```bash
verimodel scan /path/to/your/model.pkl
```

Sử dụng các tệp demo đã tạo để kiểm tra:

```bash
verimodel scan demo_models/good_model.pkl
verimodel scan demo_models/malicious_rce_model.pkl
verimodel scan demo_models/malicious_network_model.pkl
```

## 6\. 🛠️ Ngăn xếp Công nghệ (Tech Stack)

Dự án này được xây dựng với các công cụ mã nguồn mở và miễn phí.

| Thành phần | Công nghệ | Lý do lựa chọn |
| :--- | :--- | :--- |
| 🐍 Ngôn ngữ | Python 3.10+ | Hệ sinh thái AI/ML và bảo mật mạnh mẽ. |
| 🖥️ Giao diện CLI | Typer, Rich | Tạo CLI chuyên nghiệp, đẹp mắt cực kỳ nhanh chóng. |
| 📦 Quản lý Package | Poetry | Tiêu chuẩn hiện đại, thay thế `requirements.txt`. |
| 🔍 Quét Tĩnh | `pickletools` | Thư viện chuẩn của Python, an toàn để phân tích pickle. |
| 🕵️ Quét Động | `strace` (Linux), `subprocess` | Tận dụng công cụ hệ thống mạnh mẽ, không cần code sandbox phức tạp. |
| 📹 Demo | `asciinema` | Tạo file GIF demo cho README.md. |

## 7\. 🎯 Phạm vi Dự án (MVP Scope)

Đây là một dự án Sản phẩm Khả thi Tối thiểu (MVP) với mục tiêu tạo ra một công cụ ấn tượng và có khả năng trình diễn rõ ràng.

| Trong Phạm vi (In-Scope) | Ngoài Phạm vi (Out-of-Scope) |
| :--- | :--- |
| ✅ Quét tĩnh các file `.pkl`. | ❌ Hỗ trợ quét động trên Windows / macOS. |
| ✅ Quét động các file `.pkl` **chỉ trên Linux**. | ❌ Phân tích sâu các định dạng khác (`.h5`, `.onnx`). |
| ✅ Giao diện CLI (sử dụng Typer/Rich). | ❌ Hỗ trợ `.safetensors` (vì vốn đã an toàn). |
| ✅ Đóng gói thành một package Python (qua Poetry). | ❌ Giao diện người dùng Web (GUI). |
| ✅ Tạo các mô hình độc hại mẫu để demo. | ❌ Tích hợp tự động vào các hệ thống CI/CD. |

## 8\. 🌟 Tại sao dự án này quan trọng?

Dự án này giải quyết một vấn đề thực tế, cấp bách trong cộng đồng AI/ML.

Đối với hồ sơ cá nhân, đây là một "dự án điểm nhấn" hoàn hảo, chứng minh bộ kỹ năng "3 trong 1" cực kỳ hiếm:

  * **🔒 Bảo mật (Security):** Hiểu biết về lỗ hổng, phân tích bytecode, sandbox.
  * **🧠 AI/ML:** Hiểu biết về chuỗi cung ứng, các định dạng mô hình.
  * **🏗️ Kỹ thuật Phần mềm (Software Engineering):** Xây dựng công cụ CLI chuyên nghiệp, đóng gói, tài liệu.

## 9\. 📄 Giấy phép (License)

Dự án này được cấp phép theo Giấy phép MIT.
