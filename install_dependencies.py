"""
Script để cài đặt tất cả dependencies cho VeriModel.
"""

import subprocess
import sys
import os

def install_requirements():
    """Cài đặt từ requirements.txt"""
    print("📦 Đang cài đặt dependencies từ requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Cài đặt thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi cài đặt: {e}")
        return False

def check_dependencies():
    """Kiểm tra các dependencies quan trọng"""
    required = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "jinja2": "Jinja2",
        "rich": "Rich",
        "typer": "Typer"
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name} đã được cài đặt")
        except ImportError:
            print(f"❌ {name} chưa được cài đặt")
            missing.append(name)
    
    return len(missing) == 0

if __name__ == "__main__":
    print("🛡️ VeriModel - Kiểm tra và cài đặt Dependencies\n")
    
    # Kiểm tra trước
    print("1️⃣ Kiểm tra dependencies hiện tại:")
    if check_dependencies():
        print("\n✅ Tất cả dependencies đã được cài đặt!")
    else:
        print("\n⚠️  Một số dependencies chưa được cài đặt.")
        print("\n2️⃣ Đang cài đặt dependencies...")
        if install_requirements():
            print("\n3️⃣ Kiểm tra lại:")
            check_dependencies()
        else:
            print("\n❌ Cài đặt thất bại. Vui lòng chạy thủ công:")
            print("   pip install -r requirements.txt")

