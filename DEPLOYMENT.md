# 🚀 Hướng dẫn Deploy VeriModel lên Web

Tài liệu này hướng dẫn cách deploy ứng dụng VeriModel lên các nền tảng web phổ biến.

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Deploy lên Render](#deploy-lên-render)
3. [Deploy lên Railway](#deploy-lên-railway)
4. [Deploy lên Heroku](#deploy-lên-heroku)
5. [Desktop Application](#desktop-application)
6. [Cấu hình tên miền tùy chỉnh](#cấu-hình-tên-miền)
7. [Giới hạn và Lưu ý](#giới-hạn-và-lưu-ý)
8. [Checklist Demo](#checklist-demo)

---

## Tổng quan

VeriModel là một ứng dụng FastAPI có thể được deploy lên nhiều nền tảng khác nhau. Tuy nhiên, cần lưu ý một số điểm quan trọng:

### ✅ Tính năng hoạt động trên cloud:
- **Quét tĩnh (Static Scanning)**: ✅ Hoạt động đầy đủ
- **Threat Intelligence**: ✅ Hoạt động (cần API key)
- **Safetensors Converter**: ⚠️ Hoạt động nhưng có thể gặp vấn đề về kích thước với PyTorch
- **Web UI**: ✅ Hoạt động đầy đủ

### ❌ Tính năng KHÔNG hoạt động trên một số cloud platforms:
- **Quét động (Dynamic Scanning)**: ❌ Yêu cầu Docker, không khả dụng trên một số serverless platforms

---

## Deploy lên Render

Render là một nền tảng tốt cho các ứng dụng FastAPI, hỗ trợ Docker và có free tier.

### Yêu cầu:
- Tài khoản Render (đăng ký tại [render.com](https://render.com))

### Cách deploy:

1. **Tạo file `render.yaml`** (tùy chọn):
   ```yaml
   services:
     - type: web
       name: verimodel
       runtime: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn verimodel.api_server:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
         - key: VIRUSTOTAL_API_KEY
           sync: false  # Sẽ được set trong dashboard
   ```

2. **Deploy qua Dashboard:**
   - Truy cập [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect repository
   - Cấu hình:
     - **Name**: verimodel
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn verimodel.api_server:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `VIRUSTOTAL_API_KEY` (nếu cần)
   - Click "Create Web Service"

---

## Deploy lên Railway

Railway là nền tảng mới với hỗ trợ tốt cho Python và Docker.

### Cách deploy:

1. **Tạo file `railway.json`** (tùy chọn):
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn verimodel.api_server:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. **Deploy qua Dashboard:**
   - Truy cập [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Chọn repository
   - Railway sẽ tự động detect và deploy

---

## Deploy lên Heroku

Heroku là một lựa chọn cổ điển nhưng vẫn hoạt động tốt.

### Yêu cầu:
- Tài khoản Heroku
- Heroku CLI

### Cách deploy:

1. **Tạo file `Procfile`:**
   ```
   web: uvicorn verimodel.api_server:app --host 0.0.0.0 --port $PORT
   ```

2. **Tạo file `runtime.txt`:**
   ```
   python-3.11.0
   ```

3. **Deploy:**
   ```bash
   # Login
   heroku login
   
   # Tạo app
   heroku create verimodel-app
   
   # Set environment variables
   heroku config:set VIRUSTOTAL_API_KEY=your_key_here
   
   # Deploy
   git push heroku main
   ```

---

## Cấu hình tên miền

### Custom Domain Configuration

1. Vào Project Settings → Domains trên platform bạn đang sử dụng
2. Thêm domain của bạn (ví dụ: `verimodel.yourdomain.com`)
3. Thêm DNS records như hướng dẫn của platform

### Render

1. Vào Service Settings → Custom Domains
2. Add domain
3. Thêm DNS records như hướng dẫn

### Railway

1. Vào Service → Settings → Networking
2. Generate Domain hoặc Add Custom Domain
3. Cấu hình DNS theo hướng dẫn

---

## Giới hạn và Lưu ý

### Platform Limitations:

**Serverless Platforms (không hỗ trợ Docker)**:
- ⚠️ Dynamic scanning sẽ không hoạt động
- ⚠️ Có giới hạn về file size và timeout

### Render:
- ✅ **Free tier**: 750 giờ/tháng
- ⚠️ **Giới hạn**: Sleep sau 15 phút không có traffic
- ✅ **Hỗ trợ Docker**: Có thể deploy Docker container để có dynamic scanning

### Railway:
- ✅ **Free tier**: $5 credit/tháng
- ✅ **Hỗ trợ Docker**: Có thể enable Docker cho dynamic scanning

### Lưu ý quan trọng:

1. **Dynamic Scanning**: 
   - Chỉ hoạt động trên các platform hỗ trợ Docker (Render, Railway, AWS, GCP, hoặc local desktop app)
   - Trên serverless platforms không hỗ trợ Docker, tính năng này sẽ tự động bị vô hiệu hóa

2. **File Size**:
   - Các file model lớn (>10MB) có thể gặp vấn đề upload
   - Cân nhắc giới hạn kích thước file trong frontend

3. **PyTorch**:
   - PyTorch rất nặng (~500MB+), có thể làm chậm quá trình deploy
   - Cân nhắc sử dụng `torch==2.0.0+cpu` để giảm kích thước

4. **Environment Variables**:
   - Không commit API keys vào git
   - Sử dụng environment variables trong platform dashboard

5. **Security**:
   - Đảm bảo CORS được cấu hình đúng cho production
   - Sử dụng HTTPS (tự động với các platform hiện đại)

---

## Checklist Demo

### Trước khi Deploy:

- [ ] Đảm bảo code đã được test kỹ trên local
- [ ] Kiểm tra `requirements.txt` đầy đủ dependencies
- [ ] Đảm bảo có `runtime.txt` với Python version (cho web deployment)
- [ ] Kiểm tra `.gitignore` không bỏ sót file quan trọng
- [ ] Đảm bảo không commit API keys/sensitive data

### Sau khi Deploy:

- [ ] Kiểm tra health endpoint: `https://your-domain.com/api/v1/health`
- [ ] Test upload và scan file nhỏ (<1MB)
- [ ] Kiểm tra Web UI hiển thị đúng
- [ ] Test Threat Intelligence (nếu đã set API key)
- [ ] Kiểm tra console không có lỗi JavaScript
- [ ] Test trên mobile/tablet (responsive)
- [ ] Kiểm tra CORS nếu gọi API từ domain khác

### Demo Features:

- [ ] ✅ Static Scanning - Upload và quét file .pkl/.pth
- [ ] ✅ Threat Intelligence - Tra cứu hash/IP/domain (cần API key)
- [ ] ✅ Safetensors Converter - Chuyển đổi file (nếu đã cài PyTorch)
- [ ] ⚠️ Dynamic Scanning - Hiển thị message "không khả dụng trên cloud"
- [ ] ✅ Web UI - Giao diện hoạt động mượt mà
- [ ] ✅ API Documentation - Truy cập `/docs` để xem Swagger UI

### Performance:

- [ ] Kiểm tra thời gian load trang < 3 giây
- [ ] Kiểm tra thời gian scan file nhỏ < 5 giây
- [ ] Kiểm tra không có memory leak (monitor qua dashboard)

---

## Troubleshooting

### Lỗi: "ModuleNotFoundError"
- **Nguyên nhân**: Thiếu dependencies trong `requirements.txt`
- **Giải pháp**: Kiểm tra và thêm vào `requirements.txt`

### Lỗi: "Timeout"
- **Nguyên nhân**: File quá lớn hoặc xử lý lâu
- **Giải pháp**: Giảm kích thước file hoặc tăng timeout trong cấu hình server

### Lỗi: "Docker not available"
- **Nguyên nhân**: Platform không hỗ trợ Docker
- **Giải pháp**: Dynamic scanning yêu cầu Docker. Chỉ sử dụng static scanning nếu không có Docker.

### Lỗi: "File too large"
- **Nguyên nhân**: File upload vượt quá giới hạn
- **Giải pháp**: 
  - Tăng giới hạn trong cấu hình platform
  - Hoặc giới hạn kích thước file trong frontend

---

## Tài liệu tham khảo

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Tauri Documentation](https://tauri.app/)

---

## Liên hệ hỗ trợ

Nếu gặp vấn đề khi deploy, vui lòng:
1. Kiểm tra logs trong platform dashboard
2. Đọc kỹ error messages
3. Tạo issue trên GitHub repository

---

**Lưu ý cuối**: VeriModel được thiết kế để hoạt động tốt nhất với đầy đủ tính năng trên môi trường có Docker (VPS, dedicated server, hoặc cloud với Docker support). Desktop application với Tauri được khuyến nghị để có trải nghiệm tốt nhất.

