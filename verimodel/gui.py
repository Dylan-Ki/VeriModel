
import sys
import shutil
from pathlib import Path
from verimodel.static_scanner import StaticScanner
from verimodel.dynamic_scanner import DynamicScanner
from verimodel.virtual_scan_dir import create_virtual_scan_dir
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class VeriModelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ VeriModel - AI Supply Chain Firewall")
        self.console = Console()
        self.file_path = None
        self.setup_ui()

    def setup_ui(self):
        # File selection
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Label(frame, text="Chọn file pickle để quét:").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)

        # Scan options
        self.static_var = tk.BooleanVar(value=True)
        self.dynamic_var = tk.BooleanVar(value=True)
        options = tk.Frame(self.root)
        options.pack(pady=5)
        tk.Checkbutton(options, text="Quét tĩnh", variable=self.static_var).pack(side=tk.LEFT)
        tk.Checkbutton(options, text="Quét động", variable=self.dynamic_var).pack(side=tk.LEFT)
        tk.Button(options, text="Quét ngay", command=self.scan).pack(side=tk.LEFT, padx=10)

        # Output area
        self.output = scrolledtext.ScrolledText(self.root, width=90, height=30, font=("Consolas", 10))
        self.output.pack(padx=10, pady=10)
        self.output.config(state=tk.DISABLED)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl;*.pickle;*.pth")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def scan(self):
        file_path = self.file_entry.get().strip()
        if not file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file để quét!")
            return
        file_path = Path(file_path)
        if not file_path.exists():
            messagebox.showerror("Lỗi", f"File không tồn tại: {file_path}")
            return

        # Tạo thư mục ảo và copy file vào đó
        scan_dir, cleanup = create_virtual_scan_dir()
        temp_file = scan_dir / file_path.name
        try:
            shutil.copy2(file_path, temp_file)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể copy file vào thư mục tạm: {e}")
            cleanup()
            return

        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        results = {}
        if self.static_var.get():
            self.output.insert(tk.END, "[Quét tĩnh]\n")
            static_scanner = StaticScanner()
            static_result = static_scanner.scan_file(temp_file)
            results["static"] = static_result
            self.output.insert(tk.END, self.format_static(static_result) + "\n\n")
        if self.dynamic_var.get():
            self.output.insert(tk.END, "[Quét động]\n")
            dynamic_scanner = DynamicScanner()
            if not dynamic_scanner.is_supported():
                self.output.insert(tk.END, "⚠️  Quét động chỉ hỗ trợ trên Linux.\n")
            else:
                dynamic_result = dynamic_scanner.scan(str(temp_file))
                results["dynamic"] = dynamic_result
                self.output.insert(tk.END, self.format_dynamic(dynamic_result) + "\n\n")
        self.output.insert(tk.END, self.final_verdict(results))
        self.output.config(state=tk.DISABLED)
        cleanup()

    def format_static(self, result):
        if result.get("error"):
            return f"❌ {result['error']}"
        s = f"Tổng số mối đe dọa: {len(result.get('threats', []))}\n"
        for i, t in enumerate(result.get('threats', []), 1):
            s += f"  {i}. {t['type']} ({t['severity']}): {t['description']}\n"
        if result.get('warnings'):
            s += f"Cảnh báo: {len(result['warnings'])}\n"
        return s

    def format_dynamic(self, result):
        if result.get("error"):
            return f"❌ {result['error']}"
        s = f"Tổng số hành vi nguy hiểm: {len(result.get('threats', []))}\n"
        for i, t in enumerate(result.get('threats', []), 1):
            s += f"  {i}. {t['type']} ({t['severity']}): {t['description']}\n"
        return s

    def final_verdict(self, results):
        static_result = results.get("static")
        dynamic_result = results.get("dynamic")
        is_safe = True
        reasons = []
        if static_result and not static_result.get("error"):
            if not static_result["is_safe"]:
                is_safe = False
                reasons.append(f"Quét tĩnh phát hiện {len(static_result['threats'])} mối đe dọa")
        if dynamic_result and not dynamic_result.get("error"):
            if dynamic_result["is_safe"] is False:
                is_safe = False
                reasons.append(f"Quét động phát hiện {len(dynamic_result['threats'])} hành vi nguy hiểm")
        if is_safe:
            return "\n✅ KẾT LUẬN: FILE AN TOÀN\nKhông phát hiện mã độc hại hoặc hành vi nguy hiểm."
        else:
            return "\n🚨 KẾT LUẬN: FILE NGUY HIỂM\n" + "\n".join([f"  • {r}" for r in reasons]) + "\n⚠️  KHÔNG tải file này vào môi trường production!"

if __name__ == "__main__":
    root = tk.Tk()
    app = VeriModelGUI(root)
    root.mainloop()
