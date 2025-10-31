"""
Dynamic Scanner Module

Executes pickle files in a sandboxed environment and monitors system calls
to detect malicious behavior (Linux only).
"""

import os
import sys
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List


class DynamicScanner:
    """Dynamic analyzer for pickle files using strace monitoring (Linux only)."""

    # Các syscall nguy hiểm cần giám sát
    DANGEROUS_SYSCALLS = {
        "connect": "Kết nối mạng",
        "socket": "Tạo socket",
        "sendto": "Gửi dữ liệu qua mạng",
        "recvfrom": "Nhận dữ liệu từ mạng",
        "execve": "Thực thi chương trình",
        "execveat": "Thực thi chương trình (variant)",
        "fork": "Tạo process con",
        "clone": "Tạo process/thread mới",
        "open": "Mở file (có thể ghi đè file hệ thống)",
        "openat": "Mở file (variant)",
        "unlink": "Xóa file",
        "unlinkat": "Xóa file (variant)",
        "rename": "Đổi tên file",
        "renameat": "Đổi tên file (variant)",
    }

    def __init__(self):
        self.platform = platform.system()

    def is_supported(self) -> bool:
        """Kiểm tra xem nền tảng có hỗ trợ quét động không."""
        return self.platform == "Linux"

    def scan(self, file_path: str, timeout: int = 5) -> Dict:
        """
        Quét động file pickle bằng cách thực thi trong sandbox.

        Args:
            file_path: Đường dẫn đến file .pkl
            timeout: Thời gian tối đa cho phép thực thi (giây)

        Returns:
            Dict chứa kết quả quét
        """
        if not self.is_supported():
            return {
                "is_safe": None,
                "error": f"Quét động chỉ hỗ trợ trên Linux. Hệ điều hành hiện tại: {self.platform}",
                "threats": [],
                "syscalls": [],
            }

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {
                "is_safe": False,
                "error": f"File không tồn tại: {file_path}",
                "threats": [],
                "syscalls": [],
            }

        # Kiểm tra strace có tồn tại không
        if not self._check_strace():
            return {
                "is_safe": None,
                "error": "Không tìm thấy strace. Cài đặt: sudo apt-get install strace",
                "threats": [],
                "syscalls": [],
            }

        threats = []
        syscalls = []

        # Tạo file tạm để load pickle
        # Sử dụng đường dẫn tuyệt đối dạng chuỗi để tránh gọi thuộc tính trên str
        file_path_resolved = str(file_path_obj.resolve())

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as loader:
            loader_script = f"""
import sys
import pickle

try:
    with open('{file_path_resolved}', 'rb') as f:
        obj = pickle.load(f)
    print("[VeriModel] Model loaded successfully")
except Exception as e:
    print(f"[VeriModel] Error loading model: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
            loader.write(loader_script)
            loader_path = loader.name

        # Tạo file log tạm cho strace
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as log:
            log_path = log.name

        try:
            # Chạy strace
            cmd = [
                "strace",
                "-e",
                "trace=network,process,file",
                "-f",  # Follow forks
                "-o",
                log_path,
                sys.executable,
                loader_path,
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )

            # Đọc và phân tích log strace
            with open(log_path, "r") as f:
                log_content = f.read()

            # Phân tích từng dòng log
            for line in log_content.split("\n"):
                for syscall, description in self.DANGEROUS_SYSCALLS.items():
                    if syscall + "(" in line:
                        syscall_info = {
                            "syscall": syscall,
                            "description": description,
                            "log_line": line.strip(),
                        }
                        syscalls.append(syscall_info)

                        # Đánh giá mức độ nguy hiểm
                        if syscall in ["connect", "sendto", "execve", "execveat"]:
                            threats.append(
                                {
                                    "type": "DANGEROUS_SYSCALL",
                                    "severity": "HIGH",
                                    "syscall": syscall,
                                    "description": f"Phát hiện {description}",
                                    "details": line.strip(),
                                }
                            )

            # Kiểm tra stderr của script loader
            if result.returncode != 0:
                error_output = result.stderr
                if "Exception" in error_output or "Error" in error_output:
                    threats.append(
                        {
                            "type": "EXECUTION_ERROR",
                            "severity": "MEDIUM",
                            "description": "Model gây lỗi khi load",
                            "details": error_output[:200],
                        }
                    )

        except subprocess.TimeoutExpired:
            threats.append(
                {
                    "type": "TIMEOUT",
                    "severity": "HIGH",
                    "description": f"Model không hoàn thành trong {timeout} giây (có thể là vòng lặp vô hạn)",
                }
            )

        except Exception as e:
            return {
                "is_safe": False,
                "error": f"Lỗi khi quét động: {str(e)}",
                "threats": threats,
                "syscalls": syscalls,
            }

        finally:
            # Xóa file tạm
            try:
                os.unlink(loader_path)
                os.unlink(log_path)
            except:
                pass

        # Kết luận
        is_safe = len(threats) == 0

        return {
            "is_safe": is_safe,
            "threats": threats,
            "syscalls": syscalls,
            "total_syscalls": len(syscalls),
        }

    def _check_strace(self) -> bool:
        """Kiểm tra xem strace có được cài đặt không."""
        try:
            subprocess.run(["strace", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_summary(self, result: Dict) -> str:
        """Tạo tóm tắt kết quả quét."""
        if result.get("error"):
            return f"❌ LỖI: {result['error']}"

        if result["is_safe"] is None:
            return "⚠️  KHÔNG HỖ TRỢ: Quét động chỉ khả dụng trên Linux"

        threats = result.get("threats", [])

        if result["is_safe"]:
            return "✅ AN TOÀN: Không phát hiện hành vi độc hại"
        else:
            return f"🚨 NGUY HIỂM: Phát hiện {len(threats)} hành vi độc hại"