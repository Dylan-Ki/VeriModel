"""
FastAPI Server for VeriModel

RESTful API server cung cấp các endpoints để scan, convert, và query threat intelligence.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import tempfile
import shutil
import os
from datetime import datetime

from verimodel.static_scanner import StaticScanner
from verimodel.dynamic_scanner import DynamicScanner
from verimodel.threat_intelligence import ThreatIntelligence
from verimodel.safetensors_converter import SafetensorsConverter


def cleanup_file_delayed(file_path: str):
    """Cleanup file sau một khoảng thời gian để đảm bảo client đã download xong."""
    import time
    time.sleep(5)  # Đợi 5 giây
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass  # Ignore cleanup errors


app = FastAPI(
    title="VeriModel API",
    description="AI Supply Chain Firewall - REST API",
    version="0.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates và static files
templates_dir = Path(__file__).parent.parent / "web_templates"
if not templates_dir.exists():
    templates_dir.mkdir(parents=True, exist_ok=True)
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))

static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize scanners
static_scanner = StaticScanner()
dynamic_scanner = DynamicScanner()
threat_intel = ThreatIntelligence()
safetensors_converter = SafetensorsConverter()


# Pydantic models
class ScanRequest(BaseModel):
    file_path: Optional[str] = None
    static_only: bool = False
    dynamic_only: bool = False
    include_threat_intel: bool = True
    timeout: int = 5


class ConvertRequest(BaseModel):
    file_path: str
    output_path: Optional[str] = None
    safe_mode: bool = True


class ThreatIntelRequest(BaseModel):
    file_path: Optional[str] = None
    hash: Optional[str] = None
    ip: Optional[str] = None
    domain: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - Web UI."""
    template = jinja_env.get_template("index.html")
    return HTMLResponse(content=template.render())

@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {
        "service": "VeriModel API",
        "version": "0.2.0",
        "endpoints": {
            "scan": "/api/v1/scan",
            "convert": "/api/v1/convert",
            "threat-intel": "/api/v1/threat-intel",
            "health": "/api/v1/health"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "static_scanner": "available",
        "dynamic_scanner": "available" if dynamic_scanner.is_supported() else "unavailable",
        "threat_intelligence": "available" if threat_intel.vt_api_key else "no_api_key",
        "safetensors_converter": "available" if safetensors_converter.is_supported() else "unavailable"
    }


@app.post("/api/v1/scan")
async def scan_file(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    static_only: bool = Form(False),
    dynamic_only: bool = Form(False),
    include_threat_intel: bool = Form(True),
    timeout: int = Form(5)
):
    """
    Quét file để phát hiện mã độc hại.
    
    Có thể upload file hoặc cung cấp file_path (nếu file đã có trên server).
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "static": {},
        "dynamic": {},
        "threat_intelligence": {},
        "final_verdict": {}
    }

    temp_file_path = None

    try:
        # Xử lý file upload hoặc file_path
        if file:
            # Tạo file tạm thời
            suffix = Path(file.filename).suffix if file.filename else ".pkl"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            temp_file.close()
            file_path = Path(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Phải cung cấp file upload hoặc file_path")

        # Static scan
        if not dynamic_only:
            static_result = static_scanner.scan_file(file_path)
            results["static"] = static_result

        # Dynamic scan
        if not static_only:
            if dynamic_scanner.is_supported():
                dynamic_result = dynamic_scanner.scan(str(file_path), timeout=timeout)
                results["dynamic"] = dynamic_result
            else:
                results["dynamic"] = {
                    "error": "Dynamic scanning không được hỗ trợ (yêu cầu Docker)"
                }

        # Threat Intelligence
        if include_threat_intel:
            ti_result = threat_intel.analyze_file(file_path, check_vt=True)
            results["threat_intelligence"] = ti_result

        # Tính toán final verdict
        is_safe = True
        reasons = []

        if results.get("static") and not results["static"].get("error"):
            if not results["static"].get("is_safe", True):
                is_safe = False
                reasons.append(f"Static scan phát hiện {len(results['static'].get('threats', []))} mối đe dọa")

        if results.get("dynamic") and not results["dynamic"].get("error"):
            if results["dynamic"].get("is_safe") is False:
                is_safe = False
                reasons.append(f"Dynamic scan phát hiện {len(results['dynamic'].get('threats', []))} hành vi nguy hiểm")

        if results.get("threat_intelligence") and results["threat_intelligence"].get("threats"):
            is_safe = False
            reasons.append(f"Threat Intelligence phát hiện {len(results['threat_intelligence']['threats'])} mối đe dọa")

        results["final_verdict"] = {
            "is_safe": is_safe,
            "verdict": "SAFE" if is_safe else "DANGEROUS",
            "reasons": reasons
        }

        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi quét file: {str(e)}")
    finally:
        # Cleanup temp file
        if temp_file_path and os.path.exists(temp_file_path):
            background_tasks.add_task(os.unlink, temp_file_path)


@app.post("/api/v1/convert")
async def convert_to_safetensors(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    safe_mode: bool = Form(True),
    output_filename: Optional[str] = Form(None)
):
    """
    Chuyển đổi file model sang định dạng safetensors an toàn.
    """
    if not safetensors_converter.is_supported():
        raise HTTPException(
            status_code=503,
            detail="Safetensors converter không được hỗ trợ. Vui lòng cài đặt PyTorch và safetensors."
        )

    temp_file_path = None
    temp_output_path = None

    try:
        # Lưu file upload vào temp
        suffix = Path(file.filename).suffix if file.filename else ".pkl"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file_path = temp_file.name
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()

        file_path = Path(temp_file_path)

        # Xác định output path
        if output_filename:
            output_path = Path(tempfile.gettempdir()) / output_filename
        else:
            output_path = file_path.with_suffix('.safetensors')

        # Chuyển đổi
        if file_path.suffix.lower() in ['.pkl', '.pickle']:
            result = safetensors_converter.convert_pickle_to_safetensors(
                file_path, output_path, safe_mode=safe_mode
            )
        elif file_path.suffix.lower() == '.pth':
            result = safetensors_converter.convert_pytorch_to_safetensors(
                file_path, output_path
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng file không được hỗ trợ: {file_path.suffix}"
            )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Lỗi không xác định"))

        # Trả về file
        if os.path.exists(result["output_path"]):
            temp_output_path = result["output_path"]
            # Schedule cleanup sau khi response được gửi
            background_tasks.add_task(os.unlink, temp_file_path)
            background_tasks.add_task(cleanup_file_delayed, temp_output_path)
            
            return FileResponse(
                result["output_path"],
                filename=Path(result["output_path"]).name,
                media_type="application/octet-stream"
            )
        else:
            raise HTTPException(status_code=500, detail="Không tìm thấy file output")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi chuyển đổi: {str(e)}")
    finally:
        # Cleanup input file ngay lập tức nếu có lỗi
        if temp_file_path and os.path.exists(temp_file_path):
            if not (temp_output_path and os.path.exists(temp_output_path)):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass


@app.post("/api/v1/threat-intel")
async def query_threat_intelligence(
    request: ThreatIntelRequest
):
    """
    Tra cứu Threat Intelligence cho hash, IP, hoặc domain.
    """
    results = {}

    try:
        # Query hash
        if request.hash:
            results["hash"] = threat_intel.query_virustotal_hash(request.hash)

        # Query IP
        if request.ip:
            results["ip"] = threat_intel.query_virustotal_ip(request.ip)

        # Query domain
        if request.domain:
            results["domain"] = threat_intel.query_virustotal_domain(request.domain)

        # Analyze file
        if request.file_path:
            file_path = Path(request.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"File không tồn tại: {request.file_path}")
            
            ti_result = threat_intel.analyze_file(file_path, check_vt=True)
            results["file_analysis"] = ti_result

        if not results:
            raise HTTPException(
                status_code=400,
                detail="Phải cung cấp ít nhất một trong: hash, ip, domain, hoặc file_path"
            )

        return JSONResponse(content=results)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tra cứu: {str(e)}")


@app.get("/api/v1/info")
async def get_file_info(file_path: str):
    """
    Lấy thông tin về file.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File không tồn tại: {file_path}")

        file_size = path.stat().st_size
        return {
            "file_path": str(path),
            "file_name": path.name,
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "file_extension": path.suffix,
            "is_safetensors": path.suffix.lower() == ".safetensors"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VeriModel Server...")
    print("📡 Access at: http://localhost:8000 or http://127.0.0.1:8000")
    print("⚠️  Do NOT use 0.0.0.0 in browser - use localhost instead!\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

