import os
import sys
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict


class DynamicScanner:
    """Dynamic analyzer for pickle files using strace monitoring (Linux only)."""
    
    
    #Các Syscall nguy hiểm cần theo dõi
    DANGEROUS_SYSCALLS = {
        "connect": "Kết nối mạng",
        "socket": "Tạo socket mạng",
        "sendto": "Gửi dữ liệu qua mạng",
        "recvfrom": "Nhận dữ liệu từ mạng",
        "execve": "Thực thi chương trình/file nhị phân",
        "open": "Mở file(có thể ghi đè lên file  hệ thống)",
        "unlink": "Xóa file",
        "fork": "Tạo tiến trình con",
        "clone": "Tạo tiến trình, thread mới",
        "openat": "Mở file với các tùy chọn đặc biệt(variant)",
        "rename": "Đổi tên file",
        "unlinkat": "Xóa file với các tùy chọn đặc biệt(variant)",
        "unlink": "Xóa file",
        "renameat": "Đổi tên file với các tùy chọn đặc biệt(variant)",
        "rename": "Đổi tên file",
    }
    
    def __init__(self):
        self.platform = platform.system()
    
    def is_supported(self) -> bool:
        #Kiểm tra xem hệ điều hành có hỗ trợ strace không (chỉ Linux)
        return self.platform == "Linux"
    
    def scan(self, file_path: str, timeout: int = 5) -> Dict:
        """Quét động file pickle bằng thực thi sandbox.
        Args:
            file_path (str): Đường dẫn tới file pickle
            timeout (int): Thời gian chờ tối đa cho quá trình quét (giây)
            
        Returns:
            Dict: Chứa kết quả quét động (is.safe, threats, warnings, details)
        """
        
        if not self.is_supported():
            return {
                "is_safe": None,
                "threats": [],
                "error": f"Quét động chỉ hỗ trợ trên Linux. Hệ điều hành hiện tại: {self.platform}",
                "syscalls": [],
            }
            
        file_path = Path(file_path)
        if not file_pth.exists():
            return {
                "is_safe": False,
                "threats": [],
                "error": f"File không tồn tại: {file_path}",
                "syscalls": [],
            }
        
        #Kiểm tra strace có tồn tại 
        if not self._check_strace():
            return {
                "is_safe": None,
                "threats": [],
                "error": "strace không được cài đặt trên hệ thống.",
                "syscalls": [],
            }
        
        threats = []
        syscalls = []
        
        
        #Tạo file tạm để ghi log strace/load pickle
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as loader:
            loader_script = f"""
import sys
import pickle

try: 
    with open('{file_path}', 'rb') as f:
        obj = pickle.load(f)
    pri3