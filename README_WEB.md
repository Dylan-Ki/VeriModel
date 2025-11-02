# 🌐 VeriModel Web Interface - Hướng dẫn Sử dụng

Tài liệu này hướng dẫn sử dụng VeriModel qua Web Interface.

## 🚀 Khởi động Web Server

### Cách 1: Sử dụng script có sẵn (Khuyến nghị)

```bash
python run_api.py
```

### Cách 2: Sử dụng uvicorn trực tiếp

```bash
uvicorn verimodel.api_server:app --host 0.0.0.0 --port 8000 --reload
```

### Truy cập Web Interface

Sau khi khởi động server, mở trình duyệt và truy cập:

- **Web UI**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Info**: http://localhost:8000/api

⚠️ **Lưu ý quan trọng**: 
- Sử dụng `http://localhost:8000` hoặc `http://127.0.0.1:8000` trong trình duyệt
- **KHÔNG** sử dụng `http://0.0.0.0:8000` - đây chỉ là địa chỉ để server lắng nghe trên tất cả interfaces

---

## 📱 Tính năng Web Interface

### 1. 🔍 Quét File (Scan)

**Chức năng:**
- Upload file model (`.pkl`, `.pickle`, `.pth`)
- Quét tĩnh (Static Analysis)
- Quét động (Dynamic Analysis) - yêu cầu Docker
- Threat Intelligence - tra cứu IOCs trên VirusTotal

**Cách sử dụng:**
1. Chọn tab "Quét File"
2. Kéo thả file hoặc click để chọn file
3. Cấu hình tùy chọn:
   - **Chỉ quét tĩnh**: Bỏ qua quét động (nhanh hơn)
   - **Chỉ quét động**: Chỉ chạy quét động (cần Docker)
   - **Threat Intelligence**: Bật/tắt tra cứu VirusTotal
   - **Timeout**: Thời gian chờ cho quét động (giây)
4. Click "Bắt đầu Quét"
5. Xem kết quả và kết luận cuối cùng

**Kết quả hiển thị:**
- ✅ **File An Toàn**: Không phát hiện mã độc hại
- 🚨 **File Nguy Hiểm**: Phát hiện mối đe dọa, hiển thị chi tiết

### 2. 🔄 Chuyển đổi sang Safetensors

**Chức năng:**
- Chuyển đổi file `.pkl`, `.pickle`, `.pth` sang định dạng `.safetensors` an toàn

**Yêu cầu:**
- PyTorch và safetensors đã được cài đặt
- Chỉ chuyển đổi các file đã được verify an toàn!

**Cách sử dụng:**
1. Chọn tab "Chuyển đổi"
2. Upload file cần chuyển đổi
3. Click "Chuyển đổi"
4. File `.safetensors` sẽ được tải xuống tự động

**Lưu ý:**
- Quá trình chuyển đổi có thể mất thời gian với file lớn
- File output thường nhỏ hơn file input

### 3. 🕵️ Threat Intelligence

**Chức năng:**
- Tra cứu hash (MD5, SHA1, SHA256)
- Tra cứu IP address
- Tra cứu domain
- Phân tích file để trích xuất IOCs

**Yêu cầu:**
- VirusTotal API Key (tùy chọn nhưng khuyến nghị)
- Đặt API key trong sidebar hoặc environment variable `VIRUSTOTAL_API_KEY`

**Cách sử dụng:**
1. Chọn tab "Threat Intelligence"
2. Nhập một trong các giá trị:
   - **Hash**: MD5 (32 ký tự), SHA1 (40 ký tự), hoặc SHA256 (64 ký tự)
   - **IP Address**: Ví dụ `192.168.1.1`
   - **Domain**: Ví dụ `example.com`
3. Click "Tra cứu"
4. Xem kết quả từ VirusTotal

**Ví dụ Hash:**
- MD5: `5d41402abc4b2a76b9719d911017c592`
- SHA1: `aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d`
- SHA256: `2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae`

---

## ⚙️ Cấu hình

### Environment Variables

Các biến môi trường có thể được thiết lập:

```bash
# VirusTotal API Key (tùy chọn)
export VIRUSTOTAL_API_KEY="your_api_key_here"

# Python path (nếu cần)
export PYTHONPATH="/path/to/VeriModel"
```

### CORS Settings

Trong production, nên cấu hình CORS để giới hạn origins:

```python
# Trong verimodel/api_server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Thay đổi từ "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 🔧 Troubleshooting

### Lỗi: "Dynamic scanning không được hỗ trợ"

**Nguyên nhân**: Docker không được cài đặt hoặc không chạy

**Giải pháp:**
- Cài đặt Docker Desktop (Windows/Mac) hoặc Docker Engine (Linux)
- Đảm bảo Docker daemon đang chạy
- Hoặc chỉ sử dụng quét tĩnh (bật "Chỉ quét tĩnh")

### Lỗi: "VirusTotal API key không hợp lệ"

**Nguyên nhân**: API key không đúng hoặc chưa được set

**Giải pháp:**
- Lấy API key miễn phí tại [virustotal.com](https://www.virustotal.com)
- Đặt trong sidebar của Web UI
- Hoặc set environment variable: `export VIRUSTOTAL_API_KEY=your_key`

### Lỗi: "Safetensors converter không được hỗ trợ"

**Nguyên nhân**: PyTorch hoặc safetensors chưa được cài đặt

**Giải pháp:**
```bash
# Cài đặt PyTorch (CPU version - nhẹ hơn)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Cài đặt safetensors
pip install safetensors
```

### Lỗi: "File quá lớn"

**Nguyên nhân**: File upload vượt quá giới hạn

**Giải pháp:**
- Kiểm tra kích thước file (khuyến nghị < 100MB cho local)
- Tăng giới hạn upload trong code nếu cần

### Web UI không hiển thị

**Nguyên nhân**: 
- Static files không được serve đúng
- JavaScript không load

**Giải pháp:**
- Kiểm tra console trình duyệt (F12) để xem lỗi
- Đảm bảo đường dẫn `/static/app.js` có thể truy cập
- Kiểm tra network tab để xem file có load không

---

## 📊 API Endpoints

Web UI sử dụng các API endpoints sau:

### Health Check
```
GET /api/v1/health
```

### Scan File
```
POST /api/v1/scan
Content-Type: multipart/form-data

Parameters:
- file: File upload
- static_only: bool (default: false)
- dynamic_only: bool (default: false)
- include_threat_intel: bool (default: true)
- timeout: int (default: 5)
```

### Convert to Safetensors
```
POST /api/v1/convert
Content-Type: multipart/form-data

Parameters:
- file: File upload
- safe_mode: bool (default: true)
- output_filename: str (optional)
```

### Threat Intelligence
```
POST /api/v1/threat-intel
Content-Type: application/json

Body:
{
  "hash": "abc123...",
  "ip": "192.168.1.1",
  "domain": "example.com"
}
```

Xem tài liệu API đầy đủ tại: http://localhost:8000/docs

---

## 🎨 Customization

### Thay đổi giao diện

Web UI sử dụng:
- **Bootstrap 5** cho styling
- **Custom CSS** trong `web_templates/index.html`
- **JavaScript** trong `static/app.js`

Để tùy chỉnh:
1. Sửa file `web_templates/index.html` để thay đổi HTML/CSS
2. Sửa file `static/app.js` để thay đổi JavaScript logic
3. Restart server để áp dụng thay đổi

### Thay đổi port

```bash
# Sửa trong run_api.py
uvicorn.run(
    "verimodel.api_server:app",
    host="0.0.0.0",
    port=8080,  # Thay đổi port
    reload=True
)
```

---

## 🔒 Security Notes

1. **Local Development**: OK để dùng `allow_origins=["*"]`
2. **Production**: Nên giới hạn origins trong CORS
3. **API Keys**: Không commit API keys vào git
4. **File Upload**: Nên giới hạn kích thước file và kiểm tra file type
5. **HTTPS**: Sử dụng HTTPS trong production

---

## 📚 Tài liệu tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [README.md](../README.md) - Tài liệu chính
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Hướng dẫn deploy

---

## 💬 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra console trình duyệt (F12)
2. Kiểm tra server logs
3. Xem [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
4. Tạo issue trên GitHub

