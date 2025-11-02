# 🚀 VeriModel Desktop App với Tauri

Hướng dẫn setup và chạy VeriModel Desktop Application.

## Yêu cầu

1. **Rust** (cho Tauri backend)
   ```bash
   # Windows (PowerShell)
   Invoke-WebRequest https://win.rustup.rs/x86_64 -OutFile rustup-init.exe
   .\rustup-init.exe
   
   # Hoặc download từ: https://rustup.rs/
   ```

2. **Node.js** (cho Tauri CLI)
   ```bash
   # Download từ: https://nodejs.org/
   ```

3. **Python 3.10+** (cho backend)
   ```bash
   pip install -r requirements.txt
   ```

## Cài đặt

1. **Cài đặt Tauri CLI**:
   ```bash
   npm install -g @tauri-apps/cli
   ```

2. **Cài đặt dependencies**:
   ```bash
   npm install
   ```

## Chạy Development

1. **Start Python backend** (terminal 1):
   ```bash
   python run_api.py
   ```

2. **Start Tauri desktop app** (terminal 2):
   ```bash
   npm run dev
   ```

Desktop app sẽ tự động mở và kết nối với backend tại `http://localhost:8000`.

## Build Production

```bash
npm run build
```

File executable sẽ được tạo trong `src-tauri/target/release/`.

## Kiến trúc

```
Tauri Frontend (HTML/CSS/JS từ web_templates/)
  ↓
Local FastAPI Server (http://localhost:8000)
  ↓
Python Backend (verimodel/)
```

## Troubleshooting

- **Backend không khả dụng**: Đảm bảo `python run_api.py` đang chạy
- **Rust build errors**: Đảm bảo Rust toolchain đã được cài đặt đúng
- **Port 8000 bị chiếm**: Thay đổi port trong `run_api.py` và `src-tauri/src/main.rs`

