import tempfile
import shutil
from pathlib import Path

def create_virtual_scan_dir():
    """
    Tạo một thư mục tạm (ảo) để lưu file được chọn trước khi quét.
    Trả về đường dẫn thư mục tạm và hàm cleanup để xóa thư mục khi xong việc.
    """
    temp_dir = tempfile.mkdtemp(prefix="verimodel_scan_")
    def cleanup():
        shutil.rmtree(temp_dir, ignore_errors=True)
    return Path(temp_dir), cleanup

# Ví dụ sử dụng:
# scan_dir, cleanup = create_virtual_scan_dir()
# ... copy file vào scan_dir ...
# cleanup()  # Xóa thư mục tạm khi xong
