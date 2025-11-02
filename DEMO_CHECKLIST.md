# ✅ Checklist Demo VeriModel Web

Checklist này giúp đảm bảo ứng dụng sẵn sàng cho demo.

## 📋 Pre-Deployment Checklist

### Code & Configuration
- [ ] Tất cả code đã được test trên local
- [ ] Không có lỗi linter (pylint, flake8)
- [ ] `requirements.txt` đầy đủ và chính xác
- [ ] `vercel.json` đã được cấu hình đúng (nếu dùng Vercel)
- [ ] `api/index.py` tồn tại và đúng format (nếu dùng Vercel)
- [ ] `runtime.txt` có Python version (3.11)
- [ ] `.gitignore` đã cấu hình (không commit sensitive data)
- [ ] Environment variables đã được document

### Security
- [ ] Không có API keys trong code
- [ ] CORS đã được cấu hình (production nên giới hạn origins)
- [ ] File upload có giới hạn kích thước
- [ ] Input validation đã được implement

### Documentation
- [ ] README.md đã cập nhật
- [ ] DEPLOYMENT.md có hướng dẫn đầy đủ
- [ ] README_WEB.md có hướng dẫn sử dụng
- [ ] Code comments đầy đủ

---

## 🚀 Deployment Checklist

### Vercel (Khuyến nghị)
- [ ] Đã tạo tài khoản Vercel
- [ ] Đã connect GitHub repository
- [ ] Đã import project vào Vercel
- [ ] Environment variables đã được set (VIRUSTOTAL_API_KEY)
- [ ] Build thành công không có lỗi
- [ ] URL deployment đã hoạt động

### Alternative Platforms
- [ ] Render: Đã cấu hình `render.yaml` hoặc qua dashboard
- [ ] Railway: Đã cấu hình `railway.json` hoặc qua dashboard
- [ ] Heroku: Đã tạo `Procfile` và deploy

---

## 🧪 Post-Deployment Testing

### Health & Availability
- [ ] Health endpoint hoạt động: `/api/v1/health`
- [ ] Web UI load được: `/`
- [ ] API docs load được: `/docs`
- [ ] Static files load được: `/static/app.js`

### Functionality Tests

#### Static Scanning ✅
- [ ] Upload file `.pkl` nhỏ (< 1MB)
- [ ] Scan thành công và hiển thị kết quả
- [ ] Kết quả hiển thị đúng (threats, warnings)
- [ ] Final verdict hiển thị đúng

#### Threat Intelligence ✅ (nếu có API key)
- [ ] Tra cứu hash MD5 thành công
- [ ] Tra cứu IP address thành công
- [ ] Tra cứu domain thành công
- [ ] Hiển thị kết quả từ VirusTotal đúng

#### Safetensors Converter ⚠️ (nếu có PyTorch)
- [ ] Upload file `.pkl` nhỏ
- [ ] Convert thành công
- [ ] File `.safetensors` download được
- [ ] File output hợp lệ

#### Dynamic Scanning ❌ (chỉ trên platform có Docker)
- [ ] Hiển thị message "không khả dụng" đúng cách
- [ ] Không có lỗi crash khi bật dynamic scan

### User Experience
- [ ] Web UI responsive trên desktop
- [ ] Web UI responsive trên mobile
- [ ] Loading states hiển thị đúng
- [ ] Error messages rõ ràng và hữu ích
- [ ] File upload drag & drop hoạt động
- [ ] Không có lỗi JavaScript trong console
- [ ] CSS load đúng (Bootstrap 5)

### Performance
- [ ] Page load time < 3 giây
- [ ] Static scan < 5 giây (file nhỏ)
- [ ] Threat Intelligence query < 10 giây
- [ ] Không có memory leaks (monitor qua dashboard)

---

## 🌐 Custom Domain (Optional)

### DNS Configuration
- [ ] Đã thêm domain trong platform dashboard
- [ ] DNS records đã được cấu hình đúng:
  - CNAME cho subdomain: `verimodel.yourdomain.com`
  - A record cho root domain (nếu dùng root)
- [ ] SSL/TLS certificate tự động được tạo
- [ ] HTTPS redirect hoạt động

### Domain Testing
- [ ] Domain resolve đúng
- [ ] HTTPS hoạt động (certificate valid)
- [ ] Web UI load được qua custom domain
- [ ] API endpoints hoạt động qua custom domain

---

## 📊 Demo Preparation

### Demo Script
- [ ] Đã chuẩn bị file demo (safe model)
- [ ] Đã chuẩn bị file demo (malicious model - nếu có)
- [ ] Đã có sẵn VirusTotal API key để demo Threat Intelligence
- [ ] Đã test flow demo từ đầu đến cuối

### Demo Features to Show
1. ✅ **Static Scanning**
   - Upload file an toàn → Kết quả: Safe
   - Upload file độc hại → Kết quả: Dangerous (nếu có)

2. ✅ **Threat Intelligence**
   - Tra cứu hash của file
   - Tra cứu IP/Domain (nếu có)

3. ⚠️ **Safetensors Converter**
   - Chuyển đổi file (nếu đã cài PyTorch)

4. ❌ **Dynamic Scanning**
   - Giải thích tại sao không hoạt động trên cloud
   - Hiển thị message "không khả dụng"

### Backup Plan
- [ ] Có sẵn screenshot/video demo nếu live demo fail
- [ ] Đã test trên localhost để backup
- [ ] Có sẵn explanation cho các tính năng không hoạt động

---

## 🔍 Final Checks

### Documentation
- [ ] README.md có link đến deployed version
- [ ] DEPLOYMENT.md có instructions chính xác
- [ ] Code comments đầy đủ

### Monitoring
- [ ] Đã setup monitoring (nếu có)
- [ ] Đã check logs không có errors nghiêm trọng
- [ ] Đã test error handling

### Public Demo
- [ ] URL public hoạt động
- [ ] Có thể chia sẻ link cho người khác
- [ ] Không có sensitive data exposed

---

## 🎯 Quick Demo Flow

1. **Giới thiệu**: "VeriModel là công cụ bảo mật để quét file ML model..."
2. **Mở Web UI**: Truy cập deployed URL
3. **Demo Static Scan**: 
   - Upload file demo
   - Click "Bắt đầu Quét"
   - Hiển thị kết quả
4. **Demo Threat Intelligence** (nếu có API key):
   - Vào tab "Threat Intelligence"
   - Tra cứu hash hoặc IP
   - Hiển thị kết quả VirusTotal
5. **Giải thích Dynamic Scanning**:
   - "Dynamic scanning yêu cầu Docker, không khả dụng trên Vercel"
   - "Nhưng static scanning đã rất hiệu quả"
6. **Kết luận**: "VeriModel giúp bảo vệ khỏi RCE attacks trong pickle files"

---

## ❌ Known Limitations for Cloud Demo

1. **Dynamic Scanning**: Không hoạt động trên Vercel (cần Docker)
   - ✅ Workaround: Chỉ sử dụng static scanning
   - ✅ Message hiển thị rõ ràng cho user

2. **PyTorch**: Rất nặng, có thể làm chậm deploy
   - ✅ Workaround: Có thể bỏ qua PyTorch, chỉ dùng static scan
   - ✅ Safetensors converter là optional

3. **File Size**: Có giới hạn trên các platform
   - ✅ Workaround: Giới hạn kích thước file trong UI
   - ✅ Khuyến nghị: Demo với file < 10MB

---

## 📝 Notes

- ✅ = Tính năng hoạt động
- ⚠️ = Tính năng hoạt động nhưng có giới hạn
- ❌ = Tính năng không hoạt động (cần giải thích)

---

**Last Updated**: Check lại checklist này trước mỗi demo để đảm bảo mọi thứ hoạt động!

