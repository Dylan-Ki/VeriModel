# ⚡ Quick Start - Deploy VeriModel lên Web

Hướng dẫn nhanh để deploy VeriModel lên Vercel trong 5 phút.

## 🚀 Deploy lên Vercel (Khuyến nghị)

### Bước 1: Chuẩn bị Repository
Đảm bảo bạn đã có các file sau trong repository:
- ✅ `vercel.json` - Cấu hình Vercel
- ✅ `api/index.py` - Entry point cho Vercel
- ✅ `requirements.txt` - Dependencies
- ✅ `runtime.txt` - Python version

### Bước 2: Deploy qua Vercel Dashboard

1. **Truy cập**: [vercel.com](https://vercel.com)
2. **Đăng nhập** bằng GitHub/GitLab/Bitbucket
3. **Click "Add New Project"**
4. **Chọn repository** VeriModel của bạn
5. **Vercel tự động detect** cấu hình từ `vercel.json`
6. **Set Environment Variable** (tùy chọn):
   - Key: `VIRUSTOTAL_API_KEY`
   - Value: API key của bạn từ virustotal.com
7. **Click "Deploy"**
8. **Đợi build** (2-5 phút)
9. **Lấy URL**: `https://your-project.vercel.app`

### Bước 3: Kiểm tra

Truy cập:
- 🌐 **Web UI**: `https://your-project.vercel.app/`
- 📚 **API Docs**: `https://your-project.vercel.app/docs`
- ❤️ **Health Check**: `https://your-project.vercel.app/api/v1/health`

---

## 🎯 Các Platform Khác

### Render
```bash
# Tạo file render.yaml (tùy chọn)
# Deploy qua dashboard: render.com
```

### Railway
```bash
# Deploy qua dashboard: railway.app
# Tự động detect Python project
```

### Heroku
```bash
# Tạo Procfile: web: uvicorn verimodel.api_server:app --host 0.0.0.0 --port $PORT
heroku create verimodel-app
git push heroku main
```

---

## ⚠️ Lưu ý Quan trọng

1. **Dynamic Scanning** không hoạt động trên Vercel (cần Docker)
   - ✅ Static scanning vẫn hoạt động đầy đủ
   - ✅ Threat Intelligence hoạt động (cần API key)
   - ✅ Web UI hoạt động đầy đủ

2. **File Size Limits**:
   - Vercel: 4.5MB (hobby), 50MB (pro)
   - Nên giới hạn file upload trong demo

3. **PyTorch** (cho safetensors converter):
   - Rất nặng (~500MB+)
   - Có thể làm chậm build
   - Có thể bỏ qua nếu không cần converter

---

## 📚 Tài liệu Chi tiết

- 📖 **[DEPLOYMENT.md](DEPLOYMENT.md)** - Hướng dẫn đầy đủ
- 🌐 **[README_WEB.md](README_WEB.md)** - Hướng dẫn sử dụng Web UI
- ✅ **[DEMO_CHECKLIST.md](DEMO_CHECKLIST.md)** - Checklist demo

---

## 🔧 Troubleshooting Nhanh

**Build failed?**
- Kiểm tra `requirements.txt` đầy đủ
- Kiểm tra `runtime.txt` có Python version

**App không chạy?**
- Kiểm tra logs trong Vercel dashboard
- Kiểm tra `/api/v1/health` endpoint

**Dynamic scan không hoạt động?**
- ✅ Đây là hành vi bình thường trên Vercel
- Chỉ static scanning hoạt động (đã đủ hiệu quả)

---

## ✨ Demo Features

Sau khi deploy, bạn có thể demo:

1. ✅ **Static Scanning** - Upload và quét file
2. ✅ **Threat Intelligence** - Tra cứu hash/IP/domain
3. ⚠️ **Safetensors Converter** - Nếu đã cài PyTorch
4. ❌ **Dynamic Scanning** - Không khả dụng (giải thích cho audience)

---

**🎉 Chúc bạn deploy thành công!**

