"""
DEPRECATED: Tkinter GUI for VeriModel

This module is deprecated in favor of the Tauri desktop application.
The Tauri app provides a modern, cross-platform desktop experience with
better performance and a cyber-themed UI.

For desktop application, use the Tauri-based app instead.
See README.md for instructions on building and running the Tauri desktop app.

This module is kept for backward compatibility but will not be maintained.
"""

import sys
import shutil
from pathlib import Path
from verimodel.static_scanner import StaticScanner
from verimodel.dynamic_scanner import DynamicScanner
from verimodel.file_analyzer import FileAnalyzer
from verimodel.virtual_scan_dir import create_virtual_scan_dir
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Tkinter imports with deprecation warning
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError:
    tk = None
    print("⚠️ Tkinter GUI is deprecated. Please use the Tauri desktop application instead.")
    print("⚠️ Install Tauri dependencies and run: npm run dev")

class VeriModelGUI:
    """
    DEPRECATED: Use Tauri desktop app instead.
    
    This GUI is deprecated. The Tauri desktop application provides:
    - Modern cyber-themed UI
    - Better performance
    - Cross-platform support
    - Native desktop experience
    """
    def __init__(self, root):
        if tk is None:
            raise ImportError("Tkinter not available. This GUI is deprecated. Use Tauri desktop app instead.")
        
        self.root = root
        self.root.title("🛡️ VeriModel - AI Supply Chain Firewall (DEPRECATED)")
        # Show deprecation warning
        print("⚠️ WARNING: Tkinter GUI is deprecated.")
        print("⚠️ Please use the Tauri desktop application for better experience.")
        print("⚠️ See README.md for Tauri setup instructions.")
        
        self.console = Console()
        self.file_path = None
        self.analyze_file_path = None
        self.setup_ui()

    def setup_ui(self):
        # Notebook để tạo các tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tab quét
        self.scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scan_frame, text='Quét an toàn')
        
        # Tab phân tích
        self.analyze_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analyze_frame, text='Phân tích chi tiết')
        
        self.setup_scan_tab()
        self.setup_analyze_tab()

    def setup_scan_tab(self):
        # File selection
        frame = tk.Frame(self.scan_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="Chọn file pickle để quét:").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)

        # Scan options
        options = tk.Frame(self.scan_frame)
        options.pack(pady=5)
        self.static_var = tk.BooleanVar(value=True)
        self.dynamic_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options, text="Quét tĩnh", variable=self.static_var).pack(side=tk.LEFT)
        tk.Checkbutton(options, text="Quét động", variable=self.dynamic_var).pack(side=tk.LEFT)
        tk.Button(options, text="Quét ngay", command=self.scan).pack(side=tk.LEFT, padx=10)

        # Scan output area
        self.scan_output = scrolledtext.ScrolledText(self.scan_frame, width=90, height=30, font=("Consolas", 10))
        self.scan_output.pack(padx=10, pady=10)
        self.scan_output.config(state=tk.DISABLED)

    def setup_analyze_tab(self):
        # File selection for analysis
        frame = tk.Frame(self.analyze_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="Chọn file pickle để phân tích:").pack(side=tk.LEFT)
        self.analyze_file_entry = tk.Entry(frame, width=50)
        self.analyze_file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_analyze_file).pack(side=tk.LEFT)

        # Analysis button
        tk.Button(self.analyze_frame, text="🔍 Phân tích chi tiết", command=self.analyze).pack(pady=10)

        # Analysis results area with tabs
        self.analysis_notebook = ttk.Notebook(self.analyze_frame)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab cho cấu trúc file
        self.structure_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.structure_frame, text='Cấu trúc')
        self.structure_text = scrolledtext.ScrolledText(self.structure_frame, height=25, font=("Consolas", 10))
        self.structure_text.pack(fill=tk.BOTH, expand=True)

        # Tab cho thông tin entropy và byte
        self.byte_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.byte_frame, text='Thông tin Byte')
        self.byte_text = scrolledtext.ScrolledText(self.byte_frame, height=25, font=("Consolas", 10))
        self.byte_text.pack(fill=tk.BOTH, expand=True)

        # Tab cho opcodes
        self.opcode_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.opcode_frame, text='Opcodes')
        self.opcode_text = scrolledtext.ScrolledText(self.opcode_frame, height=25, font=("Consolas", 10))
        self.opcode_text.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Pickle files", "*.pkl;*.pickle;*.pth"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def browse_analyze_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Pickle files", "*.pkl;*.pickle;*.pth"), ("All files", "*.*")]
        )
        if file_path:
            self.analyze_file_path = file_path
            self.analyze_file_entry.delete(0, tk.END)
            self.analyze_file_entry.insert(0, file_path)

    def analyze(self):
        if not self.analyze_file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file để phân tích!")
            return

        try:
            analyzer = FileAnalyzer()
            file_path = Path(self.analyze_file_path)
            
            # Reset all text areas
            self.structure_text.delete(1.0, tk.END)
            self.byte_text.delete(1.0, tk.END)
            self.opcode_text.delete(1.0, tk.END)
            
            # Configure text tags for highlighting
            for text_widget in [self.structure_text, self.byte_text, self.opcode_text]:
                text_widget.tag_configure("warning", foreground="orange")
                text_widget.tag_configure("danger", foreground="red")
                text_widget.tag_configure("safe", foreground="green")
                text_widget.tag_configure("header", font=("Consolas", 11, "bold"))
            
            # Phân tích tổng thể file
            analysis_results = analyzer.analyze_file(file_path)
            if "error" in analysis_results:
                raise Exception(analysis_results["error"])

            # Hiển thị thông tin cấu trúc và mục đích
            self.structure_text.insert(tk.END, "=== THÔNG TIN CẤU TRÚC VÀ MỤC ĐÍCH FILE ===\n\n", "header")
            structure_info = analysis_results.get("structure", {})
            if structure_info:
                # Phân tích mục đích
                purpose_info = self.analyze_file_purpose(structure_info)
                self.structure_text.insert(tk.END, "PHÂN TÍCH MỤC ĐÍCH:\n", "header")
                self.structure_text.insert(tk.END, f"{purpose_info['description']}\n", 
                                        purpose_info['tag'])
                self.structure_text.insert(tk.END, f"Mức độ tin cậy: {purpose_info['trust_level']}\n\n", 
                                        purpose_info['trust_tag'])
                
                # Thông tin cấu trúc
                self.structure_text.insert(tk.END, "THÔNG TIN CẤU TRÚC:\n", "header")
                data_type = structure_info.get('structure_type', 'Không xác định')
                self.structure_text.insert(tk.END, f"- Loại dữ liệu: {data_type}\n",
                                        "warning" if data_type == "Pickle" else "safe")
                self.structure_text.insert(tk.END, f"- Protocol Pickle: {structure_info.get('protocol_version', 'Không xác định')}\n")
                total_opcodes = structure_info.get('total_opcodes', 0)
                self.structure_text.insert(tk.END, f"- Tổng số opcodes: {total_opcodes}\n",
                                        "warning" if total_opcodes > 100 else "safe")
                if 'opcode_distribution' in structure_info:
                    self.structure_text.insert(tk.END, "Phân bố Opcodes:\n")
                    for opcode, count in structure_info['opcode_distribution'].items():
                        self.structure_text.insert(tk.END, f"  {opcode}: {count}\n")

            # Hiển thị thông tin byte và entropy
            self.byte_text.insert(tk.END, "=== THÔNG TIN BYTE VÀ ENTROPY ===\n\n")
            byte_info = analysis_results.get("byte_analysis", {})
            if byte_info:
                self.byte_text.insert(tk.END, f"- Kích thước: {byte_info.get('file_size_bytes', 0):,} bytes\n")
                self.byte_text.insert(tk.END, f"- Entropy: {byte_info.get('entropy', 0):.4f}\n")
                self.byte_text.insert(tk.END, f"- Có byte null: {'Có' if byte_info.get('has_null_bytes') else 'Không'}\n")
                self.byte_text.insert(tk.END, f"- Có mã thực thi: {'Có ⚠️' if byte_info.get('has_executable_content') else 'Không'}\n\n")
                if 'byte_distribution' in byte_info:
                    self.byte_text.insert(tk.END, "Top 10 byte phổ biến nhất:\n")
                    sorted_bytes = sorted(byte_info['byte_distribution'].items(), 
                                       key=lambda x: x[1], reverse=True)[:10]
                    for byte_val, count in sorted_bytes:
                        self.byte_text.insert(tk.END, f"  Byte {byte_val}: {count} lần\n")

            # Hiển thị summary và opcodes đáng ngờ
            self.opcode_text.insert(tk.END, "=== TÓM TẮT PHÂN TÍCH ===\n\n", "header")
            summary = analyzer.get_summary()
            
            # Highlight các opcode đáng ngờ
            suspicious_opcodes = ['GLOBAL', 'REDUCE', 'EXEC', 'SYSTEM', 'LOAD', 'BUILD']
            for opcode in suspicious_opcodes:
                if opcode in summary:
                    start_idx = summary.find(opcode)
                    end_idx = start_idx + len(opcode)
                    self.opcode_text.insert(tk.END, summary[:start_idx])
                    self.opcode_text.insert(tk.END, opcode, "danger")
                    self.opcode_text.insert(tk.END, summary[end_idx:])
                    break
            else:
                self.opcode_text.insert(tk.END, summary)

            # Nếu phát hiện mã độc, hiện cảnh báo popup
            if any(opcode in summary for opcode in suspicious_opcodes):
                messagebox.showwarning(
                    "⚠️ Cảnh báo Bảo mật",
                    "File này chứa mã có thể thực thi (executable code)!\n\n" +
                    "❌ KHÔNG NÊN sử dụng file này trong môi trường production.\n" +
                    "⚠️ Chỉ sử dụng từ nguồn đáng tin cậy."
                )

        except Exception as e:
            error_msg = f"❌ Lỗi khi phân tích: {str(e)}"
            messagebox.showerror("Lỗi", f"Lỗi khi phân tích file: {str(e)}")
            for widget in [self.structure_text, self.byte_text, self.opcode_text]:
                widget.delete(1.0, tk.END)
                widget.insert(tk.END, error_msg, "danger")

    def scan(self):
        if not self.file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file để quét!")
            return

        self.scan_output.config(state=tk.NORMAL)
        self.scan_output.delete(1.0, tk.END)
        
        # Configure text tags for highlighting
        self.scan_output.tag_configure("header", font=("Consolas", 11, "bold"))
        self.scan_output.tag_configure("danger", foreground="red", font=("Consolas", 10, "bold"))
        self.scan_output.tag_configure("warning", foreground="orange")
        self.scan_output.tag_configure("safe", foreground="green")
        self.scan_output.tag_configure("info", foreground="blue")
        
        scan_dir = None
        cleanup = None
        
        try:
            # Tạo thư mục ảo an toàn để quét
            try:
                scan_dir, cleanup = create_virtual_scan_dir()
            except Exception as e:
                raise Exception(f"Không thể tạo thư mục ảo: {str(e)}")

            if not scan_dir or not scan_dir.exists():
                raise Exception("Không thể tạo thư mục ảo để quét an toàn")

            # Copy file vào thư mục ảo
            try:
                target_path = scan_dir / Path(self.file_path).name
                shutil.copy2(self.file_path, target_path)
            except Exception as e:
                raise Exception(f"Không thể copy file vào thư mục ảo: {str(e)}")

            results = {}
            
            # Quét tĩnh
            if self.static_var.get():
                self.scan_output.insert(tk.END, "[Quét tĩnh]\n")
                try:
                    static_scanner = StaticScanner()
                    static_results = static_scanner.scan_file(target_path)
                    results["static"] = static_results
                    self.scan_output.insert(tk.END, self.format_scan_results(static_results, "static") + "\n\n")
                except Exception as e:
                    self.scan_output.insert(tk.END, f"❌ Lỗi quét tĩnh: {str(e)}\n\n")

            # Quét động
            if self.dynamic_var.get():
                self.scan_output.insert(tk.END, "[Quét động]\n")
                try:
                    dynamic_scanner = DynamicScanner()
                    if not dynamic_scanner.is_supported():
                        self.scan_output.insert(tk.END, "⚠️ Quét động chỉ hỗ trợ trên Linux.\n\n")
                    else:
                        dynamic_results = dynamic_scanner.scan(str(target_path))
                        results["dynamic"] = dynamic_results
                        self.scan_output.insert(tk.END, self.format_scan_results(dynamic_results, "dynamic") + "\n\n")
                except Exception as e:
                    self.scan_output.insert(tk.END, f"❌ Lỗi quét động: {str(e)}\n\n")

            # Hiển thị kết luận cuối cùng nếu có kết quả
            if results:
                verdict = self.get_final_verdict(results)
                if verdict:
                    self.scan_output.insert(tk.END, verdict)
            else:
                self.scan_output.insert(tk.END, "\n❌ Không có kết quả quét nào thành công.")
                
        except Exception as e:
            self.scan_output.insert(tk.END, f"❌ Lỗi: {str(e)}")
        
        finally:
            # Đảm bảo dọn dẹp thư mục tạm
            if cleanup:
                try:
                    cleanup()
                except Exception as e_cleanup:
                    self.scan_output.insert(tk.END, f"\n⚠️ Lỗi khi dọn dẹp thư mục tạm: {str(e_cleanup)}")
            
            self.scan_output.config(state=tk.DISABLED)

    def format_scan_results(self, results, scan_type):
        if not results:
            return "❌ Không có kết quả quét"
        
        if isinstance(results, dict) and "error" in results:
            return f"❌ Lỗi: {results['error']}"
        
        output = []
        scan_label = "tĩnh" if scan_type == "static" else "động"
        self.scan_output.insert(tk.END, f"Kết quả quét {scan_label}:\n", "header")
        
        # Lấy threats và warnings từ đối tượng kết quả
        threats = []
        warnings = []
        
        # Nếu là dict, lấy từ key 'threats' và 'warnings'
        if isinstance(results, dict):
            threats = results.get('threats', [])
            warnings = results.get('warnings', [])
        # Nếu là object có thuộc tính threats và warnings
        else:
            threats = getattr(results, 'threats', []) if hasattr(results, 'threats') else []
            warnings = getattr(results, 'warnings', []) if hasattr(results, 'warnings') else []
        
        if threats:
            self.scan_output.insert(tk.END, f"\nPhát hiện {len(threats)} mối nguy:\n", "danger")
            for i, threat in enumerate(threats, 1):
                # Nếu threat là dict
                if isinstance(threat, dict):
                    severity = threat.get('severity', 'WARNING')
                    desc = threat.get('description', str(threat))
                # Nếu threat là object
                else:
                    severity = getattr(threat, 'severity', 'WARNING')
                    desc = getattr(threat, 'description', str(threat))
                tag = "danger" if severity.upper() == "CRITICAL" else "warning"
                self.scan_output.insert(tk.END, f"  {i}. [{severity.upper()}] {desc}\n", tag)
        else:
            self.scan_output.insert(tk.END, "✅ Không phát hiện mối nguy\n", "safe")
            
        if warnings:
            output.append(f"\nCảnh báo ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                output.append(f"  {i}. {str(warning)}")
                
        return "\n".join(output)

    def analyze_file_purpose(self, structure_info):
        """Phân tích mục đích của file dựa trên cấu trúc"""
        purpose_info = {
            'description': '',
            'trust_level': '',
            'tag': 'safe',
            'trust_tag': 'safe'
        }
        
        structure_type = structure_info.get('structure_type', '').lower()
        opcodes = structure_info.get('opcode_distribution', {})
        total_opcodes = structure_info.get('total_opcodes', 0)
        
        # Phân tích mục đích dựa trên loại file
        if 'pickle' in structure_type:
            if total_opcodes < 50:
                purpose_info['description'] = "File này có vẻ là một mô hình ML đơn giản hoặc tensor dữ liệu."
                purpose_info['trust_level'] = "Độ tin cậy cao"
            else:
                purpose_info['description'] = "⚠️ File này chứa nhiều opcode phức tạp, có thể là mô hình ML phức tạp hoặc có mã đáng ngờ."
                purpose_info['trust_level'] = "⚠️ Độ tin cậy thấp"
                purpose_info['tag'] = 'warning'
                purpose_info['trust_tag'] = 'warning'
                
        elif 'torch' in structure_type:
            if 'GLOBAL' in opcodes or 'REDUCE' in opcodes:
                purpose_info['description'] = "🚨 File này chứa mã Python có thể thực thi - CẦN THẬN TRỌNG!"
                purpose_info['trust_level'] = "🚨 KHÔNG TIN CẬY"
                purpose_info['tag'] = 'danger'
                purpose_info['trust_tag'] = 'danger'
            else:
                purpose_info['description'] = "File này có vẻ là một mô hình PyTorch bình thường."
                purpose_info['trust_level'] = "Độ tin cậy trung bình"
                
        else:
            purpose_info['description'] = "Không thể xác định chính xác mục đích của file này."
            purpose_info['trust_level'] = "Không xác định"
            purpose_info['tag'] = 'warning'
            purpose_info['trust_tag'] = 'warning'
            
        return purpose_info

    def get_final_verdict(self, results):
        if not results:
            return None
            
        is_safe = True
        warnings = []
        threats = []

        for scan_type, result in results.items():
            if not result:
                continue
                
            scan_label = "tĩnh" if scan_type == "static" else "động"
            
            # Lấy threats và warnings từ kết quả
            result_threats = []
            result_warnings = []
            
            # Nếu result là dict
            if isinstance(result, dict):
                result_threats = result.get('threats', [])
                result_warnings = result.get('warnings', [])
            # Nếu result là object
            else:
                result_threats = getattr(result, 'threats', []) if hasattr(result, 'threats') else []
                result_warnings = getattr(result, 'warnings', []) if hasattr(result, 'warnings') else []
            
            if result_threats:
                is_safe = False
                for threat in result_threats:
                    severity = threat.severity if hasattr(threat, 'severity') else 'WARNING'
                    desc = threat.description if hasattr(threat, 'description') else str(threat)
                    threats.append(f"[{severity.upper()}] {desc} (quét {scan_label})")
            
            warnings.extend([f"{str(w)} (quét {scan_label})" for w in result_warnings])

        self.scan_output.insert(tk.END, "\n=== KẾT LUẬN CUỐI CÙNG ===\n", "header")
        
        if is_safe:
            verdict = "✅ FILE AN TOÀN"
            verdict_tag = "safe"
            messagebox.showinfo("Kết quả Quét", "File này AN TOÀN để sử dụng! ✅")
        else:
            verdict = "🚨 FILE NGUY HIỂM"
            verdict_tag = "danger"
            messagebox.showwarning(
                "⚠️ Phát hiện Mã độc",
                "File này có thể NGUY HIỂM! 🚨\n\n" +
                "Lý do:\n" + "\n".join(f"• {t}" for t in threats) + "\n\n" +
                "❌ KHÔNG NÊN sử dụng file này!"
            )
            
        self.scan_output.insert(tk.END, f"\n{verdict}\n", verdict_tag)
        if is_safe:
            self.scan_output.insert(tk.END, "Không phát hiện mã độc hoặc hành vi nguy hiểm.\n", "safe")
        else:
            self.scan_output.insert(tk.END, "Lý do:\n", "danger")
            for threat in threats:
                self.scan_output.insert(tk.END, f"  • {threat}\n", "danger")
            self.scan_output.insert(tk.END, "\n⚠️ KHUYẾN CÁO: KHÔNG sử dụng file này trong môi trường production!\n", "warning")
            
            if warnings:
                self.scan_output.insert(tk.END, "\nCảnh báo:\n", "warning")
                for warning in warnings:
                    self.scan_output.insert(tk.END, f"  • {warning}\n", "warning")
                    
        return None

def main():
    root = tk.Tk()
    # Set window icon
    try:
        ico_path = Path(__file__).parent / "shield.ico"
        if ico_path.exists():
            root.iconbitmap(ico_path)
    except:
        pass  # Skip icon if not found
        
    # Center window
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    app = VeriModelGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
