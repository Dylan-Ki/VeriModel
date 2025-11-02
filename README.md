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

**VeriModel** cung cấp **nhiều lớp phân tích bảo mật**:

### 1️⃣ Static Analysis (Quét Tĩnh)
- Phân tích bytecode pickle **mà không thực thi**
- Phát hiện các opcode và import nguy hiểm (ví dụ: `os.system`, `subprocess.run`)
- Sử dụng YARA rules để phát hiện patterns độc hại
- An toàn 100% - không có rủi ro thực thi mã

### 2️⃣ Dynamic Analysis (Quét Động)
- Thực thi mô hình trong **Docker sandbox** được cách ly hoàn toàn
- Phát hiện hành vi thực tế: kết nối mạng, thực thi lệnh, ghi file
- Hỗ trợ trên tất cả hệ điều hành có Docker

### 3️⃣ Threat Intelligence
- Tự động trích xuất IOCs (hashes, IPs, domains) từ file
- Tra cứu VirusTotal API để phát hiện các indicator đã biết
- Hỗ trợ tra cứu hash, IP address, và domain

### 4️⃣ Safetensors Converter
- Chuyển đổi các file model từ pickle sang định dạng safetensors an toàn
- Hỗ trợ `.pkl`, `.pickle`, và `.pth` files
- Bảo vệ bạn khỏi các cuộc tấn công RCE trong tương lai

---

## 🚀 Cài đặt

### Yêu cầu

- Python 3.10 trở lên
- Docker (cho quét động - tùy chọn)
- VirusTotal API Key (cho Threat Intelligence - tùy chọn)

### Cài đặt nhanh

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Hoặc sử dụng script tự động
python install_dependencies.py
```

### Cài đặt từng phần (nếu gặp lỗi)

```bash
# Core dependencies (bắt buộc)
pip install fastapi uvicorn jinja2 python-multipart

# CLI dependencies
pip install rich typer

# Scanner dependencies
pip install yara-python docker requests

# Safetensors converter (tùy chọn)
pip install safetensors torch
```

### Kiểm tra cài đặt

```bash
python -c "import uvicorn, fastapi, jinja2; print('✅ OK')"
```

---

## 📖 Sử dụng

### 🖥️ Web Interface (Khuyến nghị)

```bash
# Chạy server
python run_api.py

# Mở trình duyệt: http://localhost:8000
# ⚠️ KHÔNG dùng http://0.0.0.0:8000 trong trình duyệt!
```

Web interface cung cấp:
- Upload và quét file trực tiếp
- Chuyển đổi sang safetensors
- Tra cứu Threat Intelligence
- Giao diện hiện đại với Bootstrap 5

### 💻 Command Line Interface

```bash
# Quét đầy đủ (static + dynamic)
verimodel scan model.pkl

# Chỉ quét tĩnh (nhanh hơn)
verimodel scan model.pkl --static-only

# Chỉ quét động
verimodel scan model.pkl --dynamic-only

# Với Threat Intelligence
verimodel scan model.pkl --threat-intel

# Quét với chi tiết đầy đủ
verimodel scan model.pkl --verbose

# Chuyển đổi sang safetensors
verimodel convert model.pkl

# Tra cứu Threat Intelligence
verimodel threat-intel --hash <hash> --ip <ip> --domain <domain>

# Xem thông tin file
verimodel info model.pkl
```

### 🌐 API Endpoints

Nếu muốn tích hợp vào ứng dụng của bạn:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Scan file
curl -X POST -F "file=@model.pkl" http://localhost:8000/api/v1/scan

# Convert to safetensors
curl -X POST -F "file=@model.pkl" http://localhost:8000/api/v1/convert -o output.safetensors

# Threat Intelligence
curl -X POST -H "Content-Type: application/json" \
  -d '{"hash":"abc123..."}' \
  http://localhost:8000/api/v1/threat-intel
```

Xem tài liệu API đầy đủ tại: http://localhost:8000/docs (Swagger UI)

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
│   ├── __init__.py                # Package initialization
│   ├── cli.py                     # CLI interface (Typer + Rich)
│   ├── api_server.py              # FastAPI server với Web UI
│   ├── static_scanner.py          # Static bytecode analysis với YARA
│   ├── dynamic_scanner.py         # Dynamic Docker sandbox execution
│   ├── threat_intelligence.py     # VirusTotal integration
│   ├── safetensors_converter.py   # Safe model conversion
│   └── rules/
│       └── pickle.yar             # YARA rules
├── web_templates/
│   └── index.html                 # Web UI template
├── static/
│   └── app.js                     # Frontend JavaScript
├── demo_models/                   # Demo pickle files
├── run_api.py                     # Script chạy server
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

### Tech Stack

- **Python 3.10+**: Core language
- **FastAPI + Uvicorn**: Modern web framework và ASGI server
- **Jinja2**: Template engine cho Web UI
- **Typer + Rich**: Professional CLI với output đẹp
- **YARA**: Pattern matching cho static analysis
- **Docker**: Sandbox cho dynamic analysis
- **VirusTotal API**: Threat Intelligence
- **Safetensors**: Safe model format

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

- **Quét động yêu cầu Docker**: Cần Docker đang chạy để sử dụng dynamic scanning
- **Threat Intelligence yêu cầu API key**: VirusTotal API key cần thiết (miễn phí từ virustotal.com)
- **Safetensors converter yêu cầu PyTorch**: Cần cài đặt torch và safetensors
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

- [README_WEB.md](README_WEB.md) - Hướng dẫn chi tiết về Web Interface
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Xử lý các lỗi thường gặp
- [BUGFIXES.md](BUGFIXES.md) - Log các bug fixes và improvements

### Liên kết ngoài

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
