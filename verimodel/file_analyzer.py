"""
File Analyzer Module

Phân tích chi tiết cấu trúc và nội dung của file pickle.
"""

import pickle
import pickletools
import io
from pathlib import Path
from typing import Dict, List

class FileAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        
    def analyze_file(self, file_path: Path) -> Dict:
        """
        Phân tích chi tiết file pickle.
        
        Args:
            file_path: Đường dẫn tới file cần phân tích
            
        Returns:
            Dict chứa kết quả phân tích
        """
        if not file_path.exists():
            return {
                "error": f"File không tồn tại: {file_path}"
            }
            
        try:
            # Thông tin cơ bản về file
            file_info = {
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "format": file_path.suffix,
                "directory": str(file_path.parent)
            }
            
            # Phân tích cấu trúc pickle
            structure_info = self._analyze_pickle_structure(file_path)
            
            # Phân tích byte sequences
            byte_info = self._analyze_byte_sequences(file_path)
            
            # Tổng hợp kết quả
            self.analysis_results = {
                "file_info": file_info,
                "structure": structure_info,
                "byte_analysis": byte_info
            }
            
            return self.analysis_results
            
        except Exception as e:
            return {
                "error": f"Lỗi khi phân tích file: {str(e)}"
            }
            
    def _analyze_pickle_structure(self, file_path: Path) -> Dict:
        """Phân tích cấu trúc và protocol của pickle."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Phân tích protocol
            protocol = pickle.HIGHEST_PROTOCOL
            if content:
                protocol = content[0] if content[0] <= pickle.HIGHEST_PROTOCOL else -1
                
            # Phân tích opcodes
            opcodes = list(pickletools.genops(io.BytesIO(content)))
            opcode_stats = {}
            for op, arg, pos in opcodes:
                if op.name not in opcode_stats:
                    opcode_stats[op.name] = 0
                opcode_stats[op.name] += 1
                
            return {
                "protocol_version": protocol,
                "total_opcodes": len(opcodes),
                "opcode_distribution": opcode_stats,
                "structure_type": self._determine_structure_type(opcodes)
            }
            
        except Exception as e:
            return {"error": f"Lỗi khi phân tích cấu trúc: {str(e)}"}
            
    def _analyze_byte_sequences(self, file_path: Path) -> Dict:
        """Phân tích chuỗi bytes trong file."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Phân tích phân phối bytes
            byte_dist = {}
            for b in content:
                if b not in byte_dist:
                    byte_dist[b] = 0
                byte_dist[b] += 1
                
            # Tính entropy
            entropy = self._calculate_entropy(byte_dist, len(content))
            
            return {
                "file_size_bytes": len(content),
                "entropy": entropy,
                "byte_distribution": byte_dist,
                "has_null_bytes": 0 in byte_dist,
                "has_executable_content": self._check_executable_content(content)
            }
            
        except Exception as e:
            return {"error": f"Lỗi khi phân tích bytes: {str(e)}"}
            
    def _determine_structure_type(self, opcodes) -> str:
        """Xác định loại cấu trúc dữ liệu trong pickle."""
        opnames = [op[0].name for op in opcodes]
        if 'DICT' in opnames:
            return "Dictionary"
        elif 'LIST' in opnames:
            return "List/Array"
        elif 'GLOBAL' in opnames:
            return "Custom Object"
        else:
            return "Simple Value"
            
    def _calculate_entropy(self, byte_dist: Dict, total_bytes: int) -> float:
        """Tính entropy của file dựa trên phân phối bytes."""
        import math
        entropy = 0
        for count in byte_dist.values():
            prob = count / total_bytes
            entropy -= prob * math.log2(prob)
        return entropy
        
    def _check_executable_content(self, content: bytes) -> bool:
        """Kiểm tra có dấu hiệu của mã thực thi."""
        # Kiểm tra magic numbers của PE, ELF, hoặc Mach-O
        exe_signatures = [
            b'MZ',  # Windows PE
            b'\x7fELF',  # Linux ELF
            b'\xca\xfe\xba\xbe',  # Mach-O
            b'\xcf\xfa\xed\xfe'  # Mach-O 64-bit
        ]
        return any(sig in content for sig in exe_signatures)
        
    def get_summary(self) -> str:
        """Tạo bản tóm tắt kết quả phân tích."""
        if not self.analysis_results:
            return "❌ Chưa có kết quả phân tích"
            
        if "error" in self.analysis_results:
            return f"❌ LỖI: {self.analysis_results['error']}"
            
        file_info = self.analysis_results["file_info"]
        structure = self.analysis_results["structure"]
        byte_analysis = self.analysis_results["byte_analysis"]
        
        summary = [
            "📊 KẾT QUẢ PHÂN TÍCH CHI TIẾT",
            f"- Tên file: {file_info['name']}",
            f"- Kích thước: {file_info['size']:,} bytes",
            f"- Loại dữ liệu: {structure['structure_type']}",
            f"- Protocol pickle: {structure['protocol_version']}",
            f"- Tổng số opcodes: {structure['total_opcodes']}",
            f"- Entropy: {byte_analysis['entropy']:.2f}",
            f"- Có mã thực thi: {'Có' if byte_analysis['has_executable_content'] else 'Không'}"
        ]
        
        return "\n".join(summary)