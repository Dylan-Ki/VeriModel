# 🚀 Hướng dẫn Deploy VeriModel lên Web

Tài liệu này hướng dẫn cách deploy ứng dụng VeriModel lên các nền tảng web phổ biến.

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Deploy lên Vercel (Khuyến nghị)](#deploy-lên-vercel)
3. [Deploy lên Render](#deploy-lên-render)
4. [Deploy lên Railway](#deploy-lên-railway)
5. [Deploy lên Heroku](#deploy-lên-heroku)
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

### ❌ Tính năng KHÔNG hoạt động trên cloud:
- **Quét động (Dynamic Scanning)**: ❌ Yêu cầu Docker, không khả dụng trên Vercel/Render/Heroku

---

## Deploy lên Vercel

Vercel là nền tảng phổ biến nhất cho các ứng dụng FastAPI với deploy miễn phí và hiệu năng tốt.

### Yêu cầu:
- Tài khoản Vercel (đăng ký tại [vercel.com](https://vercel.com))
- Git repository trên GitHub/GitLab/Bitbucket
- Node.js (để cài đặt Vercel CLI - tùy chọn)

### Cách 1: Deploy qua Vercel Dashboard (Khuyến nghị)

1. **Chuẩn bị repository:**
   ```bash
   # Đảm bảo các file sau đã có trong repo:
   # - vercel.json
   # - api/index.py
   # - requirements.txt
   # - runtime.txt
   ```

2. **Đăng nhập Vercel:**
   - Truy cập [vercel.com](https://vercel.com)
   - Đăng nhập bằng GitHub/GitLab/Bitbucket

3. **Import Project:**
   - Click "Add New Project"
   - Chọn repository VeriModel
   - Vercel sẽ tự động phát hiện cấu hình từ `vercel.json`

4. **Cấu hình Environment Variables (Tùy chọn):**
   - Trong Project Settings → Environment Variables
   - Thêm `VIRUSTOTAL_API_KEY` nếu muốn sử dụng Threat Intelligence

5. **Deploy:**
   - Click "Deploy"
   - Đợi quá trình build hoàn tất (thường 2-5 phút)

6. **Lấy URL:**
   - Sau khi deploy xong, bạn sẽ có URL dạng: `https://your-project.vercel.app`
   - URL này có thể được sử dụng ngay hoặc cấu hình tên miền tùy chỉnh

### Cách 2: Deploy qua Vercel CLI

```bash
# Cài đặt Vercel CLI (cần Node.js)
npm i -g vercel

# Đăng nhập
vercel login

# Deploy
vercel

# Deploy production
vercel --prod
```

### Cấu trúc file cần thiết:

```
VeriModel/
├── api/
│   └── index.py          # Entry point cho Vercel
├── vercel.json           # Cấu hình Vercel
├── requirements.txt      # Python dependencies
├── runtime.txt           # Python version
└── verimodel/            # Source code
```

---

## Deploy lên Render

Render là một nền tảng thay thế tốt cho Vercel, hỗ trợ Docker và có free tier.

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

### Vercel

1. Vào Project Settings → Domains
2. Thêm domain của bạn (ví dụ: `verimodel.yourdomain.com`)
3. Thêm DNS records như hướng dẫn:
   - CNAME: `verimodel` → `cname.vercel-dns.com`
   - Hoặc A record nếu dùng root domain

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

### Vercel:
- ✅ **Free tier**: 100GB bandwidth/tháng, unlimited requests
- ⚠️ **Giới hạn**: 
  - Function timeout: 60 giây (hobby), 300 giây (pro)
  - File upload: 4.5MB (hobby), 50MB (pro)
  - Memory: 1GB (hobby), 3GB (pro)
- ❌ **Không hỗ trợ Docker**: Dynamic scanning sẽ không hoạt động

### Render:
- ✅ **Free tier**: 750 giờ/tháng
- ⚠️ **Giới hạn**: Sleep sau 15 phút không có traffic
- ✅ **Hỗ trợ Docker**: Có thể deploy Docker container để có dynamic scanning

### Railway:
- ✅ **Free tier**: $5 credit/tháng
- ✅ **Hỗ trợ Docker**: Có thể enable Docker cho dynamic scanning

### Lưu ý quan trọng:

1. **Dynamic Scanning**: 
   - Chỉ hoạt động trên các platform hỗ trợ Docker (Render, Railway, AWS, GCP)
   - Trên Vercel, tính năng này sẽ tự động bị vô hiệu hóa và hiển thị thông báo

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
   - Sử dụng HTTPS (tự động với Vercel/Render/Railway)

---

## Checklist Demo

### Trước khi Deploy:

- [ ] Đảm bảo code đã được test kỹ trên local
- [ ] Kiểm tra `requirements.txt` đầy đủ dependencies
- [ ] Đảm bảo có `vercel.json` (nếu dùng Vercel)
- [ ] Đảm bảo có `api/index.py` (nếu dùng Vercel)
- [ ] Đảm bảo có `runtime.txt` với Python version
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
- **Giải pháp**: Tăng timeout trong `vercel.json` hoặc giảm kích thước file

### Lỗi: "Docker not available"
- **Nguyên nhân**: Đang deploy trên Vercel (không hỗ trợ Docker)
- **Giải pháp**: Đây là hành vi bình thường. Dynamic scanning sẽ tự động bị disable.

### Lỗi: "File too large"
- **Nguyên nhân**: File upload vượt quá giới hạn
- **Giải pháp**: 
  - Tăng giới hạn trong cấu hình platform
  - Hoặc giới hạn kích thước file trong frontend

---

## Tài liệu tham khảo

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)

---

## Liên hệ hỗ trợ

Nếu gặp vấn đề khi deploy, vui lòng:
1. Kiểm tra logs trong platform dashboard
2. Đọc kỹ error messages
3. Tạo issue trên GitHub repository

---

**Lưu ý cuối**: VeriModel được thiết kế để hoạt động tốt nhất với đầy đủ tính năng trên môi trường có Docker (VPS, dedicated server, hoặc cloud với Docker support). Deploy lên serverless platforms như Vercel sẽ chỉ hỗ trợ Static Scanning và Threat Intelligence.

