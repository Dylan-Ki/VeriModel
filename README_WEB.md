# 🛡️ VeriModel Web Interface

Giao diện web hiện đại cho VeriModel sử dụng FastAPI + HTML/JavaScript thay vì Streamlit.

## 🚀 Cách chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy FastAPI server

```bash
python run_api.py
```

Hoặc:

```bash
uvicorn verimodel.api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Truy cập giao diện

⚠️ **QUAN TRỌNG:** Sử dụng một trong các địa chỉ sau:
- **http://localhost:8000** ✅ (Khuyến nghị)
- **http://127.0.0.1:8000** ✅

❌ **KHÔNG** sử dụng `http://0.0.0.0:8000` trong trình duyệt - sẽ gặp lỗi ERR_ADDRESS_INVALID!

## ✨ Tính năng

- **Quét File**: Upload và quét file pickle để phát hiện mã độc hại
- **Chuyển đổi**: Chuyển đổi file sang định dạng safetensors an toàn
- **Threat Intelligence**: Tra cứu hash/IP/domain trên VirusTotal

## 📁 Cấu trúc

```
web_templates/
  └── index.html          # Template HTML chính

static/
  └── app.js             # JavaScript cho giao diện

verimodel/
  └── api_server.py      # FastAPI server với endpoints
```

## 🔧 API Endpoints

- `GET /` - Giao diện web
- `POST /api/v1/scan` - Quét file
- `POST /api/v1/convert` - Chuyển đổi file
- `POST /api/v1/threat-intel` - Tra cứu Threat Intelligence
- `GET /api/v1/health` - Health check

## 💡 Lưu ý

- Đảm bảo Docker đang chạy nếu muốn sử dụng quét động
- Đặt `VIRUSTOTAL_API_KEY` environment variable để sử dụng Threat Intelligence
- Giao diện sử dụng Bootstrap 5 và không cần Streamlit

