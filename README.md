# 🛡️ VeriModel - AI Supply Chain Firewall

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**VeriModel** là một công cụ bảo mật CLI (Command-Line Interface) được thiết kế để quét và phát hiện mã độc hại trong các file mô hình AI dựa trên pickle (`.pkl`, `.pth`). Công cụ này hoạt động như một "tường lửa" cho chuỗi cung ứng AI/ML, bảo vệ bạn khỏi các cuộc tấn công Remote Code Execution (RCE) tiềm ẩn.

---

## 🎯 Vấn đề

Ngành công nghiệp AI/ML đang phát triển bùng nổ với hàng triệu mô hình được chia sẻ trên các nền tảng như Hugging Face, GitHub. Phần lớn các mô hình này sử dụng định dạng **pickle** của Python - một định dạng serialization **vốn dĩ không an toàn**.

### Tại sao pickle nguy hiểm?

Khi bạn tải một file pickle từ nguồn không tin cậy bằng `pickle.load()`, bạn thực chất đang **thực thi mã tùy ý** từ file đó. Điều này có thể dẫn đến:

- 🚨 **Remote Code Execution (RCE)**: Kẻ tấn công chiếm quyền kiểm soát hệ thống
- 🌐 **Exfiltration dữ liệu**: Đánh cắp thông tin nhạy cảm
- 💣 **Backdoor**: Cài đặt mã độc vĩnh viễn
- 🔓 **Privilege escalation**: Leo thang đặc quyền

---

## 💡 Giải pháp

**VeriModel** cung cấp **hai lớp phân tích bảo mật**:

### 1️⃣ Static Analysis (Quét Tĩnh)
- Phân tích bytecode pickle **mà không thực thi**
- Phát hiện các opcode và import nguy hiểm (ví dụ: `os.system`, `subprocess.run`)
- An toàn 100% - không có rủi ro thực thi mã

### 2️⃣ Dynamic Analysis (Quét Động) - _Chỉ Linux_
- Thực thi mô hình trong môi trường **sandbox được giám sát**
- Sử dụng `strace` để theo dõi system calls
- Phát hiện hành vi thực tế: kết nối mạng, thực thi lệnh, ghi file

---

## 🚀 Cài đặt

### Yêu cầu

- Python 3.10 trở lên
- Linux (cho quét động - tùy chọn)
- `strace` (cho quét động trên Linux)

### Cài đặt từ source

```bash
# Clone repository
git clone https://github.com/yourusername/verimodel.git
cd verimodel

# Cài đặt Poetry (nếu chưa có)
curl -sSL https://install.python-poetry.org | python3 -

# Cài đặt dependencies
poetry install

# Kích hoạt virtual environment
poetry shell
```

### Cài đặt strace (cho Linux)

```bash
# Ubuntu/Debian
sudo apt-get install strace

# Fedora/RHEL
sudo dnf install strace

# Arch Linux
sudo pacman -S strace
```

---

## 📖 Sử dụng

### Quét một file pickle

```bash
# Quét đầy đủ (static + dynamic)
verimodel scan model.pkl

# Chỉ quét tĩnh (nhanh hơn, an toàn hơn)
verimodel scan model.pkl --static-only

# Chỉ quét động (Linux only)
verimodel scan model.pkl --dynamic-only

# Quét với chi tiết đầy đủ
verimodel scan model.pkl --verbose

# Quét với timeout tùy chỉnh
verimodel scan model.pkl --timeout 10
```

### Xem thông tin file

```bash
verimodel info model.pkl
```

### Hiển thị phiên bản

```bash
verimodel --version
```

---

## 🧪 Demo

### Tạo các file demo

Dự án bao gồm một script để tạo các file pickle độc hại cho mục đích demo:

```bash
python generate_malicious_models.py
```

Script này sẽ tạo ra 5 file trong thư mục `demo_models/`:

1. ✅ `good_model.pkl` - Model an toàn (baseline)
2. 🚨 `malicious_rce_model.pkl` - RCE payload (os.system)
3. 🚨 `malicious_network_model.pkl` - Network connection
4. 🚨 `malicious_filewrite_model.pkl` - File system write
5. 🚨 `malicious_subprocess_model.pkl` - Subprocess spawn

### Chạy demo

```bash
# Quét file an toàn
verimodel scan demo_models/good_model.pkl

# Quét file RCE
verimodel scan demo_models/malicious_rce_model.pkl

# Quét file network
verimodel scan demo_models/malicious_network_model.pkl -v
```

### Kết quả mẫu

**File an toàn:**
```
✅ KẾT LUẬN: FILE AN TOÀN
Không phát hiện mã độc hại hoặc hành vi nguy hiểm.
```

**File độc hại:**
```
🚨 KẾT LUẬN: FILE NGUY HIỂM
  • Quét tĩnh phát hiện 2 mối đe dọa
  • Quét động phát hiện 1 hành vi nguy hiểm

⚠️  KHUYẾN NGHỊ:
  • KHÔNG tải (load) file này vào môi trường production
  • Xem xét nguồn gốc của file
  • Sử dụng định dạng an toàn hơn như .safetensors
```

---

## 🏗️ Kiến trúc

```
verimodel/
├── verimodel/
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # CLI interface (Typer + Rich)
│   ├── static_scanner.py     # Static bytecode analysis
│   └── dynamic_scanner.py    # Dynamic sandbox execution
├── demo_models/              # Demo pickle files
├── generate_malicious_models.py  # Demo file generator
├── pyproject.toml            # Poetry configuration
└── README.md                 # This file
```

### Tech Stack

- **Python 3.10+**: Core language
- **Typer + Rich**: Professional CLI with beautiful output
- **Poetry**: Modern dependency management
- **pickletools**: Safe pickle bytecode analysis
- **strace**: System call monitoring (Linux)

---

## 🔍 Cách hoạt động

### Static Scanner

1. Mở file pickle ở chế độ binary read
2. Sử dụng `pickletools.genops()` để duyệt bytecode
3. Tìm kiếm các GLOBAL opcode (import statements)
4. So sánh với danh sách đen các hàm nguy hiểm
5. Phát hiện REDUCE opcode (có thể thực thi)

**Danh sách đen bao gồm:**
- `os.system`, `os.popen`, `os.exec*`
- `subprocess.*`
- `eval`, `exec`, `compile`
- `socket.socket`, `urllib.*`, `requests.*`

### Dynamic Scanner (Linux only)

1. Tạo script loader tạm thời
2. Thực thi script với `strace` để monitor syscalls
3. Phân tích log để tìm các syscall nguy hiểm:
   - `connect`, `sendto` (network)
   - `execve`, `fork`, `clone` (process)
   - `open`, `unlink`, `rename` (file operations)
4. Báo cáo các hành vi đáng ngờ

---

## ⚠️ Giới hạn

- **Quét động chỉ hỗ trợ Linux**: Windows/macOS không hỗ trợ strace
- **Không phân tích .safetensors**: Định dạng này đã an toàn từ thiết kế
- **Không hỗ trợ .h5, .onnx**: Chỉ tập trung vào pickle
- **False positives có thể xảy ra**: Một số model hợp lệ có thể trigger cảnh báo
- **Không thể phát hiện 100%**: Kẻ tấn công tinh vi có thể bypass

---

## 🤝 Đóng góp

Contributions are welcome! Vui lòng:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

---

## 📜 License

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

## 🙏 Acknowledgments

- **Pickle Security Research**: Các nghiên cứu về lỗ hổng pickle
- **Hugging Face**: Cảm hứng từ các vấn đề an toàn mô hình
- **Python Security Community**: Các best practices và patterns

---

## 📚 Tài liệu tham khảo

- [Python Pickle Documentation](https://docs.python.org/3/library/pickle.html)
- [Exploiting Python Pickles](https://davidhamann.de/2020/04/05/exploiting-python-pickle/)
- [ML Model Security](https://github.com/EthicalML/awesome-production-machine-learning#model-security)

---

## 💬 Liên hệ

**Tác giả**: Your Name

**Email**: your.email@example.com

**GitHub**: [@yourusername](https://github.com/yourusername)

---

## ⭐ Star History

Nếu dự án này hữu ích cho bạn, hãy cho nó một ⭐ trên GitHub!

---

**Disclaimer**: Công cụ này được tạo ra cho mục đích giáo dục và nghiên cứu. Không sử dụng để tấn công hoặc làm hại hệ thống của người khác. Tác giả không chịu trách nhiệm về việc sử dụng sai mục đích.
