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
        
    def scan_file(self, file_path: Path) -> Dict:
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
                "error": f"File không đúng định dạng: {file_path}",
                "threats": [],
                "warnings": [],
                "details": [],
            }

        threats = []
        warnings = []
        details = []

        try:
            with open(file_path, "rb") as f:
                # Phân tích bytecode pickle
                opcodes = list(pickletools.genops(f))

                for opcode, arg, pos in opcodes:
                    detail = {
                        "position": pos,
                        "opcode": opcode.name,
                        "arg": str(arg) if arg else None,
                    }
                    details.append(detail)

                    module_func = None
                    if opcode.name == "GLOBAL":
                        module_func = arg if isinstance(arg, str) else None
                        # Kiểm tra trong danh sách đen
                        if module_func and any(dangerous in module_func for dangerous in self.DANGEROUS_IMPORTS):
                            threats.append(
                                {
                                    "type": "DANGEROUS_IMPORT",
                                    "severity": "HIGH",
                                    "description": f"Phát hiện import đáng ngờ/nguy hiểm: {module_func}",
                                    "position": pos,
                                    "opcode": opcode.name,
                                    "argument": module_func,
                                }
                            )
                    elif opcode.name == "REDUCE":
                        # REDUCE có thể thực thi hàm, kiểm tra arg nếu là str
                        module_func = arg if isinstance(arg, str) else None
                        if module_func and any(susp in module_func for susp in self.SUSPICIOUS_IMPORTS):
                            warnings.append(
                                {
                                    "type": "SUSPICIOUS_IMPORT",
                                    "severity": "MEDIUM",
                                    "description": f"Phát hiện import nghi ngờ: {module_func}",
                                    "position": pos,
                                    "opcode": opcode.name,
                                    "argument": module_func,
                                }
                            )

        except Exception as e:
            return {
                "is_safe": False,
                "error": f"Lỗi khi quét file: {str(e)}",
                "threats": [],
                "warnings": [],
                "details": [],
            }

        # Kết luận
        is_safe = len(threats) == 0

        return {
            "is_safe": is_safe,
            "threats": threats,
            "warnings": warnings,
            "details": details,
            "total_threats": len(threats),
        }
        
    def get_summary(self, result: Dict) -> str:
        """Tạo tóm tắt kết quả quét tĩnh
        Args:
            result (Dict): Kết quả quét tĩnh từ scan_file
        Returns:
            str: Tóm tắt kết quả quét
        """
        if result.get("error"):
            return f"❌ LỖI: {result['error']}"
        
        
        threats = result.get("threats", [])
        warnings = result.get("warnings", [])
        
        
        if result["is_safe"]:
            if warnings:
                return f"⚠️  CẢNH BÁO: Tìm thấy {len(warnings)} cảnh báo (không chắc chắn nguy hiểm)"
            else:
                return "✅ AN TOÀN: Không phát hiện mã độc hại"
        else:
            return f"🚨 NGUY HIỂM: Phát hiện {len(threats)} mối đe dọa"