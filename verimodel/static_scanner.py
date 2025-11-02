"""
Static Scanner Module (Vercel-compatible)

Đảm bảo YARA rules được load đúng trên Vercel serverless environment.
"""

import pickletools
from pathlib import Path
from typing import List, Dict, Tuple
import yara
import zipfile
import io
import os

# Tìm đường dẫn YARA rules (hỗ trợ cả local và Vercel)
def find_yara_rules_path():
    """Tìm đường dẫn đến YARA rules file."""
    # Thử các đường dẫn có thể có
    possible_paths = [
        Path(__file__).parent / "rules" / "pickle.yar",  # Local development
        Path("/var/task/verimodel/rules/pickle.yar"),    # Vercel serverless
        Path(os.getcwd()) / "verimodel" / "rules" / "pickle.yar",  # Alternative
        Path("/var/task") / "verimodel" / "rules" / "pickle.yar",  # Vercel absolute
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ Found YARA rules at: {path}")
            return path
    
    # Nếu không tìm thấy, trả về None thay vì raise error
    print(f"⚠️ YARA rules không tìm thấy. Đã thử:")
    for p in possible_paths:
        print(f"  - {p} (exists: {p.exists()})")
    print(f"Current directory: {os.getcwd()}")
    print(f"__file__ location: {Path(__file__).parent}")
    
    # List files để debug
    try:
        task_dir = Path("/var/task")
        if task_dir.exists():
            print(f"Files in /var/task:")
            for item in task_dir.rglob("*.yar"):
                print(f"  - {item}")
    except Exception as e:
        print(f"Cannot list /var/task: {e}")
    
    return None  # Trả về None thay vì raise error


class StaticScanner:
    """Phân tích tĩnh file pickle bằng YARA và pickletools."""
    
    def __init__(self):
        self.findings: list[Dict] = []
        try:
            yara_rules_path = find_yara_rules_path()
            self.yara_rules = yara.compile(filepath=str(yara_rules_path))
            print(f"✅ YARA rules loaded from: {yara_rules_path}")
        except FileNotFoundError as e:
            print(f"❌ YARA rules không tìm thấy: {e}")
            self.yara_rules = None
        except Exception as e:
            print(f"❌ Lỗi khi compile YARA rules: {e}")
            self.yara_rules = None

    def _scan_content(self, content: bytes, file_name: str) -> Tuple[List, List, List]:
        """Quét nội dung file (bytes) bằng YARA và pickletools."""
        threats = []
        warnings = []
        details = []

        # 1. Quét bằng YARA
        if self.yara_rules:
            try:
                matches = self.yara_rules.match(data=content)
                for match in matches:
                    severity = match.meta.get("severity", "MEDIUM").upper()
                    threat_entry = {
                        "type": f"YARA:{match.rule}",
                        "severity": severity,
                        "description": match.meta.get("description", "Không có mô tả"),
                        "file_context": file_name,
                    }
                    if severity in ["HIGH", "CRITICAL"]:
                        threats.append(threat_entry)
                    else:
                        warnings.append(threat_entry)
            except Exception as e:
                warnings.append({
                    "type": "YARA_ERROR",
                    "severity": "LOW",
                    "description": f"Lỗi khi quét YARA: {e}",
                    "file_context": file_name,
                })
        else:
            warnings.append({
                "type": "YARA_UNAVAILABLE",
                "severity": "LOW",
                "description": "YARA rules không khả dụng. Chỉ quét bằng pickletools.",
                "file_context": file_name,
            })

        # 2. Phân tích Opcodes
        try:
            opcodes = list(pickletools.genops(io.BytesIO(content)))
            details = [
                {
                    "position": pos,
                    "opcode": opcode.name,
                    "arg": str(arg) if arg else None,
                }
                for opcode, arg, pos in opcodes
            ]
        except Exception:
            pass 
            
        return threats, warnings, details

    def scan_file(self, file_path: Path) -> Dict:
        """Quét tĩnh file (pickle, pth, hoặc các định dạng khác)."""
        self.findings = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "is_safe": False,
                "error": f"File không tồn tại: {file_path}",
                "threats": [], "warnings": [], "details": [],
            }

        all_threats = []
        all_warnings = []
        all_details = []

        try:
            file_suffix = file_path.suffix.lower()

            # Xử lý file .pth (là file ZIP)
            if file_suffix == ".pth":
                try:
                    with zipfile.ZipFile(file_path, 'r') as zf:
                        for sub_file_name in zf.namelist():
                            if sub_file_name.endswith(('.pkl', '/data.pkl', '.pickle')):
                                content = zf.read(sub_file_name)
                                threats, warnings, details = self._scan_content(
                                    content, 
                                    f"{file_path.name}/{sub_file_name}"
                                )
                                all_threats.extend(threats)
                                all_warnings.extend(warnings)
                                all_details.extend(details)
                except zipfile.BadZipFile:
                    # Nếu không phải zip, coi nó là file pickle thường
                    content = file_path.read_bytes()
                    threats, warnings, details = self._scan_content(content, file_path.name)
                    all_threats.extend(threats)
                    all_warnings.extend(warnings)
                    all_details.extend(details)

            # Xử lý các file pickle khác
            elif file_suffix in [".pkl", ".pickle"]:
                content = file_path.read_bytes()
                threats, warnings, details = self._scan_content(content, file_path.name)
                all_threats.extend(threats)
                all_warnings.extend(warnings)
                all_details.extend(details)
            
            else:
                # Quét bất kỳ file nào khác
                content = file_path.read_bytes()
                threats, warnings, details = self._scan_content(content, file_path.name)
                all_threats.extend(threats)
                all_warnings.extend(warnings)
                all_details.extend(details)

        except Exception as e:
            return {
                "is_safe": False,
                "error": f"Lỗi khi quét file: {str(e)}",
                "threats": [], "warnings": [], "details": [],
            }

        # Kết luận
        is_safe = len(all_threats) == 0

        return {
            "is_safe": is_safe,
            "threats": all_threats,
            "warnings": all_warnings,
            "details": all_details,
            "total_opcodes": len(all_details),
            "total_threats": len(all_threats),
        }

    def get_summary(self, result: Dict) -> str:
        """Tạo tóm tắt kết quả quét tĩnh."""
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
