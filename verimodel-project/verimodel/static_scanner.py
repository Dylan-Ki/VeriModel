import pickletools
from pathlib import Path
from typing import List, Dict, Tuple


class StaticScanner:
    """Static analyzer for pickle files using bytecode inspection."""
    
    #Danh sách đen các module/hàm nguy hiểm
    DANGEROUS_IMPORTS = {
        "os.system",
        "os.popen",
        "os.execv",
        "os.execve",
        "os.execl",
        "os.execlp",
        "os.execlp",
        "os.spawn",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_output",
        "eval",
        "exec",
        "compile",
        "__builtin__.eval",
        "__builtin__.exec",
        "__builtin__.compile",
        "socket.socket",
        "urllib.request.urlopen",
        "urllib.request.Request",
        "requests.get",
        "requests.post",
        "http.client.HTTPConnection",
        "http.client.HTTPSConnection",
    }
    
    #Các module nghi ngờ ( cảnh báo nhưng chưa chắc đã gay hại )
    SUSPICIOUS_IMPORTS = {
        "pickle",
        "dill",
        "cloudpickle",
        "torch.load",
        "tensorflow.keras.models.load_model",
    }
    
    def __init__(self):
        self.findings: list[Dict] = []
        
    def scan_file(self, file_path: str) -> Dict:
        """Quét tĩnh file pickle
        Args:
            file_path (str): Đường dẫn tới file pickle
            Returns:
                Dict: Chứa kết quả quét tĩnh (is.safe, threats, warnings, details)
                """
            self.findings = []
            file_path = Path(file_path)
            
            if not file_path.suffix.lower() in [".pkl", ".pickle", ".pth"]:
                return {
                    "is_safe": False,
                    "error": "File không tồn tại: {file_path}",
                    "threats": [],
                    "warnings": [],
                    "details": [],
                }
            if 