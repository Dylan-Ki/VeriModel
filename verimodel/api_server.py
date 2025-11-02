"""
FastAPI Server for VeriModel

API server với Web UI để quét và phân tích file model AI.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile
import shutil
import os
from datetime import datetime

# ===== SAFE IMPORTS =====
# Import từng module một, catch errors
try:
    from jinja2 import Environment, FileSystemLoader
    JINJA_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Jinja2 import failed: {e}")
    JINJA_AVAILABLE = False

try:
    from verimodel.static_scanner import StaticScanner
    STATIC_SCANNER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ StaticScanner import failed: {e}")
    STATIC_SCANNER_AVAILABLE = False
    StaticScanner = None

try:
    from verimodel.threat_intelligence import ThreatIntelligence
    THREAT_INTEL_AVAILABLE = True
except Exception as e:
    print(f"⚠️ ThreatIntelligence import failed: {e}")
    THREAT_INTEL_AVAILABLE = False
    ThreatIntelligence = None

# Dynamic scanner and converter are optional
DYNAMIC_AVAILABLE = False
CONVERTER_AVAILABLE = False

# ===== APP INITIALIZATION =====
app = FastAPI(
    title="VeriModel API",
    description="AI Supply Chain Firewall",
    version="0.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== SETUP TEMPLATES & STATIC =====
templates_dir = Path(__file__).parent.parent / "web_templates"
static_dir = Path(__file__).parent.parent / "static"

if JINJA_AVAILABLE and templates_dir.exists():
    jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
else:
    jinja_env = None
    print("⚠️ Templates not available")

if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    except Exception as e:
        print(f"⚠️ Static files mount failed: {e}")

# ===== INITIALIZE SCANNERS =====
static_scanner = None
threat_intel = None

if STATIC_SCANNER_AVAILABLE:
    try:
        static_scanner = StaticScanner()
        print("✅ Static scanner initialized")
    except Exception as e:
        print(f"❌ Static scanner init failed: {e}")

if THREAT_INTEL_AVAILABLE:
    try:
        threat_intel = ThreatIntelligence()
        print("✅ Threat intel initialized")
    except Exception as e:
        print(f"❌ Threat intel init failed: {e}")


# ===== ROUTES =====

@app.get("/")
async def root():
    """Root endpoint."""
    if jinja_env:
        try:
            template = jinja_env.get_template("index.html")
            return HTMLResponse(content=template.render())
        except Exception as e:
            return HTMLResponse(f"""
            <html><body>
            <h1>🛡️ VeriModel API</h1>
            <p>Template error: {e}</p>
            <p><a href="/docs">API Documentation</a></p>
            </body></html>
            """)
    else:
        return HTMLResponse("""
        <html><body>
        <h1>🛡️ VeriModel API</h1>
        <p>Web UI not available. Use <a href="/docs">API Documentation</a></p>
        </body></html>
        """)


@app.get("/api")
async def api_info():
    """API info."""
    return {
        "service": "VeriModel API",
        "version": "0.2.0",
        "status": "running",
        "components": {
            "static_scanner": STATIC_SCANNER_AVAILABLE,
            "threat_intel": THREAT_INTEL_AVAILABLE,
            "dynamic_scanner": DYNAMIC_AVAILABLE,
            "converter": CONVERTER_AVAILABLE
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "platform": "local",
        "static_scanner": "available" if static_scanner else "unavailable",
        "threat_intelligence": "available" if threat_intel else "unavailable",
        "dynamic_scanner": "available" if DYNAMIC_AVAILABLE else "unavailable",
        "safetensors_converter": "available" if CONVERTER_AVAILABLE else "unavailable"
    }


@app.post("/api/v1/scan")
async def scan_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    static_only: bool = Form(False),
    include_threat_intel: bool = Form(True),
):
    """Scan file for malicious code."""
    
    if not static_scanner:
        raise HTTPException(
            status_code=503,
            detail="Static scanner not available. Check deployment logs."
        )
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "platform": "local",
        "static": {},
        "threat_intelligence": {},
        "final_verdict": {}
    }

    temp_file_path = None

    try:
        # Save uploaded file
        suffix = Path(file.filename).suffix if file.filename else ".pkl"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file_path = temp_file.name
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        file_path = Path(temp_file_path)

        # Static scan
        static_result = static_scanner.scan_file(file_path)
        results["static"] = static_result

        # Threat Intelligence
        if include_threat_intel and threat_intel:
            ti_result = threat_intel.analyze_file(file_path, check_vt=True)
            results["threat_intelligence"] = ti_result

        # Final verdict
        is_safe = True
        reasons = []

        if results["static"] and not results["static"].get("error"):
            if not results["static"].get("is_safe", True):
                is_safe = False
                threats_count = len(results["static"].get("threats", []))
                reasons.append(f"Static scan: {threats_count} threats detected")

        if results.get("threat_intelligence", {}).get("threats"):
            is_safe = False
            ti_count = len(results["threat_intelligence"]["threats"])
            reasons.append(f"Threat Intelligence: {ti_count} threats detected")

        results["final_verdict"] = {
            "is_safe": is_safe,
            "verdict": "SAFE" if is_safe else "DANGEROUS",
            "reasons": reasons
        }

        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scan error: {str(e)}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            background_tasks.add_task(os.unlink, temp_file_path)


@app.post("/api/v1/threat-intel")
async def query_threat_intelligence(
    hash: str = Form(None),
    ip: str = Form(None),
    domain: str = Form(None)
):
    """Query threat intelligence."""
    
    if not threat_intel:
        raise HTTPException(
            status_code=503,
            detail="Threat Intelligence not available"
        )
    
    results = {}

    try:
        if hash:
            results["hash"] = threat_intel.query_virustotal_hash(hash)
        if ip:
            results["ip"] = threat_intel.query_virustotal_ip(ip)
        if domain:
            results["domain"] = threat_intel.query_virustotal_domain(domain)

        if not results:
            raise HTTPException(
                status_code=400,
                detail="Provide at least one: hash, ip, or domain"
            )

        return JSONResponse(content=results)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query error: {str(e)}"
        )


# ===== STARTUP EVENT =====
@app.on_event("startup")
async def startup_event():
    """Log startup info."""
    print("=" * 50)
    print("🚀 VeriModel API Starting...")
    print(f"✅ FastAPI: OK")
    print(f"{'✅' if STATIC_SCANNER_AVAILABLE else '❌'} Static Scanner: {'OK' if static_scanner else 'FAILED'}")
    print(f"{'✅' if THREAT_INTEL_AVAILABLE else '❌'} Threat Intel: {'OK' if threat_intel else 'FAILED'}")
    print(f"{'✅' if DYNAMIC_AVAILABLE else '❌'} Dynamic Scanner: {'OK' if DYNAMIC_AVAILABLE else 'Not available'}")
    print(f"{'✅' if CONVERTER_AVAILABLE else '❌'} Converter: {'OK' if CONVERTER_AVAILABLE else 'Not available'}")
    print("=" * 50)
