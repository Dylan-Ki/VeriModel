"""
Dynamic Scanner Module (Nâng cấp v2.0)

Thực thi file pickle trong một Docker sandbox được cách ly hoàn toàn.
Yêu cầu: Docker daemon đang chạy.
"""

import os
import sys
import platform
import subprocess
import tempfile
try:
    import docker  # Thư viện mới
    from docker.errors import ImageNotFound, BuildError, APIError, DockerException, ReadTimeout  # type: ignore
except Exception:
    # Docker SDK not available — allow module to import so static analysis/CI doesn't fail.
    docker = None
    # Provide simple fallback exception classes used in the code so names exist.
    class ImageNotFound(Exception): pass
    class BuildError(Exception): pass
    class APIError(Exception): pass
    class DockerException(Exception): pass
    class ReadTimeout(Exception): pass
from pathlib import Path
from typing import Dict, List

# Tên image sandbox
SANDBOX_IMAGE_NAME = "verimodel-sandbox:latest"

class DynamicScanner:
    """
    Phân tích động bằng cách thực thi file trong Docker sandbox.
    """

    def __init__(self):
        self.platform = platform.system()
        # Nếu Docker SDK không thể import, biến `docker` sẽ là None — tránh gọi from_env trên None
        if docker is None:
            self.docker_client = None
        else:
            try:
                self.docker_client = docker.from_env()
            except DockerException:
                self.docker_client = None

    def is_supported(self) -> bool:
        """Kiểm tra xem Docker có sẵn và đang chạy không."""
        if not self.docker_client:
            return False
        try:
            self.docker_client.ping()
            return True
        except APIError:
            return False

    def _build_sandbox_image(self):
        """Build Docker image cho sandbox nếu nó chưa tồn tại."""
        if not self.docker_client:
            # Docker client không có sẵn (ví dụ: Docker SDK không cài đặt hoặc khởi tạo thất bại)
            return False

        try:
            self.docker_client.images.get(SANDBOX_IMAGE_NAME)
            return True  # Image đã tồn tại
        except ImageNotFound:
            pass  # Cần build image

        dockerfile_content = """
FROM python:3.10-slim
RUN useradd --create-home --shell /bin/bash verimodel
WORKDIR /home/verimodel
USER verimodel
COPY loader_script.py .
CMD ["python", "loader_script.py"]
"""
        try:
            # Tạo bối cảnh build tạm thời
            with tempfile.TemporaryDirectory() as temp_dir:
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")
                loader_script_path = os.path.join(temp_dir, "loader_script.py")
                
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)
                
                # Tạo file loader_script.py rỗng (nó sẽ được ghi đè lúc chạy)
                with open(loader_script_path, "w") as f:
                    f.write("# Placeholder for loader script")

                print(f"Đang build image sandbox '{SANDBOX_IMAGE_NAME}'...")
                self.docker_client.images.build(
                    path=temp_dir,
                    tag=SANDBOX_IMAGE_NAME,
                    rm=True
                )
            print("Build image thành công.")
            return True
        except BuildError as e:
            print(f"Lỗi khi build image sandbox: {e}")
            return False
        except APIError as e:
            print(f"Lỗi API Docker: {e}")
            return False

    def scan(self, file_path: str, timeout: int = 10) -> Dict:
        """
        Quét động file pickle bằng cách thực thi trong Docker sandbox.
        """
        if not self.is_supported():
            return {
                "is_safe": None,
                "error": "Quét động yêu cầu Docker đang chạy. Vui lòng khởi động Docker.",
                "threats": [],
                "details": "",
            }

        # Đảm bảo image sandbox đã được build
        if not self._build_sandbox_image():
            return {
                "is_safe": False,
                "error": f"Không thể build image sandbox '{SANDBOX_IMAGE_NAME}'.",
                "threats": [],
                "details": "",
            }

        file_path_obj = Path(file_path).resolve()
        if not file_path_obj.exists():
            return {
                "is_safe": False,
                "error": f"File không tồn tại: {file_path}",
                "threats": [],
                "details": "",
            }

        threats = []
        logs = ""

        # Tạo file loader script tạm thời
        loader_script = f"""
import sys
import pickle
import os

# Tên file bên trong container
MODEL_FILE = '/tmp/model/{file_path_obj.name}'

if not os.path.exists(MODEL_FILE):
    print(f"[VeriModel] Lỗi: Không tìm thấy file model trong container tại {{MODEL_FILE}}", file=sys.stderr)
    sys.exit(1)

try:
    with open(MODEL_FILE, 'rb') as f:
        obj = pickle.load(f)
    # Nếu load thành công, chúng ta không in gì ra stdout
    # Bất kỳ output nào cũng có thể là dấu hiệu (ví dụ: mã độc in "OK")
    print("[VeriModel] Model loaded successfully", file=sys.stderr)
except Exception as e:
    # Đây là nơi quan trọng: nếu pickle.load() thất bại VÌ MÃ ĐỘC,
    # nó có thể in ra stderr.
    print(f"[VeriModel] Error loading model: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        
        container = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(loader_script)
                loader_path_host = f.name

            if not self.docker_client:
                raise RuntimeError("Docker client is not available.")

            container = self.docker_client.containers.run(
                SANDBOX_IMAGE_NAME,
                command=["python", "/tmp/loader_script.py"],
                volumes={
                    str(file_path_obj.parent): {"bind": "/tmp/model", "mode": "ro"},
                    loader_path_host: {"bind": "/tmp/loader_script.py", "mode": "ro"}
                },
                network_mode="none", # Vô hiệu hóa mạng
                cap_drop=["ALL"],    # Bỏ tất cả kernel capabilities
                mem_limit="256m",    # Giới hạn bộ nhớ
                detach=True,
            )

            # Đợi container thực thi với timeout
            result = None
            returncode = -1
            try:
                result = container.wait(timeout=timeout)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")
                # Phân tích kết quả
                returncode = result.get('StatusCode', -1) if isinstance(result, dict) else -1
            except (subprocess.TimeoutExpired, ReadTimeout):
                container.kill()
                threats.append({
                    "type": "TIMEOUT",
                    "severity": "HIGH",
                    "description": f"Model không hoàn thành trong {timeout} giây (có thể là vòng lặp vô hạn hoặc hành vi đáng ngờ)",
                })
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")
                returncode = -1
            
            if returncode != 0:
                threats.append({
                    "type": "EXECUTION_ERROR",
                    "severity": "MEDIUM",
                    "description": "Model gây lỗi khi load (có thể do mã độc hoặc file bị hỏng)",
                    "details": logs,
                })
            
            # Mã độc có thể `print()` ra stdout
            if "[VeriModel] Model loaded successfully" not in logs and returncode == 0:
                 threats.append({
                    "type": "SUSPICIOUS_OUTPUT",
                    "severity": "MEDIUM",
                    "description": "Script loader không chạy như mong đợi, có thể bị can thiệp.",
                    "details": logs,
                })

        except Exception as e:
            return {
                "is_safe": False,
                "error": f"Lỗi khi chạy Docker sandbox: {str(e)}",
                "threats": threats,
                "details": logs,
            }
        finally:
            if container:
                container.remove(force=True)
            if 'loader_path_host' in locals() and os.path.exists(loader_path_host):
                os.unlink(loader_path_host)

        # Kết luận
        is_safe = len(threats) == 0

        return {
            "is_safe": is_safe,
            "threats": threats,
            "details": logs,
        }

    def get_summary(self, result: Dict) -> str:
        """Tạo tóm tắt kết quả quét."""
        if result.get("error"):
            return f"❌ LỖI: {result['error']}"

        if result["is_safe"] is None:
            return "⚠️  KHÔNG HỖ TRỢ: Quét động yêu cầu Docker đang chạy"

        threats = result.get("threats", [])

        if result["is_safe"]:
            return "✅ AN TOÀN: Không phát hiện hành vi độc hại trong sandbox"
        else:
            return f"🚨 NGUY HIỂM: Phát hiện {len(threats)} hành vi độc hại/bất thường trong sandbox"