"""
FastAPI Server for VeriModel (Vercel-compatible version)

Tối ưu cho Vercel deployment: Chỉ hỗ trợ Static Scan và Threat Intelligence.
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
from verimodel.threat_intelligence import ThreatIntelligence

# Conditional imports
try:
    from verimodel.dynamic_scanner import DynamicScanner
    DYNAMIC_AVAILABLE = True
except Exception:
    DYNAMIC_AVAILABLE = False
    DynamicScanner = None

try:
    from verimodel.safetensors_converter import SafetensorsConverter
    CONVERTER_AVAILABLE = True
except Exception:
    CONVERTER_AVAILABLE = False
    SafetensorsConverter = None


def cleanup_file_delayed(file_path: str):
    """Cleanup file sau một khoảng thời gian."""
    import time
    time.sleep(5)
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass


app = FastAPI(
    title="VeriModel API",
    description="AI Supply Chain Firewall - REST API (Vercel Edition)",
    version="0.2.0-vercel"
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

# Initialize scanners (chỉ những gì có sẵn)
static_scanner = StaticScanner()
dynamic_scanner = DynamicScanner() if DYNAMIC_AVAILABLE else None
threat_intel = ThreatIntelligence()
safetensors_converter = SafetensorsConverter() if CONVERTER_AVAILABLE else None


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
        "service": "VeriModel API (Vercel Edition)",
        "version": "0.2.0-vercel",
        "platform": "Vercel Serverless",
        "endpoints": {
            "scan": "/api/v1/scan",
            "convert": "/api/v1/convert",
            "threat-intel": "/api/v1/threat-intel",
            "health": "/api/v1/health"
        },
        "limitations": {
            "dynamic_scan": "Not available on Vercel (requires Docker)",
            "file_size": "4.5MB (hobby tier) / 50MB (pro tier)",
            "timeout": "60 seconds (hobby) / 300 seconds (pro)"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "platform": "Vercel",
        "static_scanner": "available",
        "dynamic_scanner": "unavailable (Docker not supported on Vercel)",
        "threat_intelligence": "available" if threat_intel.vt_api_key else "no_api_key",
        "safetensors_converter": "available" if (CONVERTER_AVAILABLE and safetensors_converter and safetensors_converter.is_supported()) else "unavailable",
        "note": "Dynamic scanning requires Docker and is not available on Vercel serverless platform"
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
    
    ⚠️ Trên Vercel: Chỉ hỗ trợ Static Scan và Threat Intelligence.
    Dynamic Scan yêu cầu Docker (không khả dụng trên Vercel).
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "platform": "Vercel",
        "static": {},
        "dynamic": {},
        "threat_intelligence": {},
        "final_verdict": {}
    }

    temp_file_path = None

    try:
        if file:
            suffix = Path(file.filename).suffix if file.filename else ".pkl"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            temp_file.close()
            file_path = Path(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Phải cung cấp file upload")

        # Static scan (luôn available)
        if not dynamic_only:
            static_result = static_scanner.scan_file(file_path)
            results["static"] = static_result

        # Dynamic scan (không khả dụng trên Vercel)
        if not static_only:
            if dynamic_scanner and dynamic_scanner.is_supported():
                # Trường hợp hiếm: có Docker (không xảy ra trên Vercel)
                dynamic_result = dynamic_scanner.scan(str(file_path), timeout=timeout)
                results["dynamic"] = dynamic_result
            else:
                results["dynamic"] = {
                    "error": "Dynamic scanning không khả dụng trên Vercel (yêu cầu Docker). Vui lòng sử dụng Static Scan.",
                    "is_safe": None,
                    "threats": [],
                    "details": "Vercel serverless platform không hỗ trợ Docker containers."
                }

        # Threat Intelligence
        if include_threat_intel:
            ti_result = threat_intel.analyze_file(file_path, check_vt=True)
            results["threat_intelligence"] = ti_result

        # Tính toán final verdict (chỉ dựa trên static + TI)
        is_safe = True
        reasons = []

        if results.get("static") and not results["static"].get("error"):
            if not results["static"].get("is_safe", True):
                is_safe = False
                reasons.append(f"Static scan phát hiện {len(results['static'].get('threats', []))} mối đe dọa")

        # Dynamic scan results bị bỏ qua vì không khả dụng

        if results.get("threat_intelligence") and results["threat_intelligence"].get("threats"):
            is_safe = False
            reasons.append(f"Threat Intelligence phát hiện {len(results['threat_intelligence']['threats'])} mối đe dọa")

        results["final_verdict"] = {
            "is_safe": is_safe,
            "verdict": "SAFE" if is_safe else "DANGEROUS",
            "reasons": reasons,
            "note": "Verdict chỉ dựa trên Static Scan và Threat Intelligence (Dynamic Scan không khả dụng trên Vercel)"
        }

        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi quét file: {str(e)}")
    finally:
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
    
    ⚠️ Trên Vercel: Tính năng này có thể không khả dụng nếu PyTorch chưa được cài đặt
    (do kích thước package quá lớn).
    """
    if not CONVERTER_AVAILABLE or not safetensors_converter:
        raise HTTPException(
            status_code=503,
            detail="Safetensors converter không được hỗ trợ trên deployment này. PyTorch chưa được cài đặt (do kích thước quá lớn cho Vercel)."
        )
    
    if not safetensors_converter.is_supported():
        raise HTTPException(
            status_code=503,
            detail="Safetensors converter không được hỗ trợ. Vui lòng cài đặt PyTorch và safetensors."
        )

    temp_file_path = None
    temp_output_path = None

    try:
        suffix = Path(file.filename).suffix if file.filename else ".pkl"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file_path = temp_file.name
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()

        file_path = Path(temp_file_path)

        if output_filename:
            output_path = Path(tempfile.gettempdir()) / output_filename
        else:
            output_path = file_path.with_suffix('.safetensors')

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

        if os.path.exists(result["output_path"]):
            temp_output_path = result["output_path"]
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
    """Tra cứu Threat Intelligence cho hash, IP, hoặc domain."""
    results = {}

    try:
        if request.hash:
            results["hash"] = threat_intel.query_virustotal_hash(request.hash)

        if request.ip:
            results["ip"] = threat_intel.query_virustotal_ip(request.ip)

        if request.domain:
            results["domain"] = threat_intel.query_virustotal_domain(request.domain)

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
    """Lấy thông tin về file."""
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
    print("🚀 Starting VeriModel Server (Vercel Edition)...")
    print("📡 Access at: http://localhost:8000")
    print("⚠️  Note: Dynamic scanning is disabled (Vercel doesn't support Docker)\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
