"""
Streamlit Web UI for VeriModel

Giao diện web hiện đại để quét, chuyển đổi, và tra cứu threat intelligence.
"""

import streamlit as st
from pathlib import Path
import tempfile
import os
import json
from datetime import datetime

from verimodel.static_scanner import StaticScanner
from verimodel.dynamic_scanner import DynamicScanner
from verimodel.threat_intelligence import ThreatIntelligence
from verimodel.safetensors_converter import SafetensorsConverter


# Page config
st.set_page_config(
    page_title="VeriModel - AI Supply Chain Firewall",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-safe {
        color: #28a745;
        font-weight: bold;
    }
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "scanner" not in st.session_state:
    st.session_state.scanner = StaticScanner()
if "dynamic_scanner" not in st.session_state:
    st.session_state.dynamic_scanner = DynamicScanner()
if "threat_intel" not in st.session_state:
    st.session_state.threat_intel = ThreatIntelligence()
if "converter" not in st.session_state:
    st.session_state.converter = SafetensorsConverter()


def main():
    """Main application."""
    st.markdown('<p class="main-header">🛡️ VeriModel - AI Supply Chain Firewall</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Cấu hình")
        
        # VirusTotal API Key
        vt_api_key = st.text_input(
            "VirusTotal API Key",
            type="password",
            help="Nhập API key của VirusTotal để kích hoạt Threat Intelligence (tùy chọn)",
            key="vt_api_key_input"
        )
        if vt_api_key:
            os.environ["VIRUSTOTAL_API_KEY"] = vt_api_key
            st.session_state.threat_intel = ThreatIntelligence(virustotal_api_key=vt_api_key)
            st.session_state.vt_api_key = vt_api_key
        elif "vt_api_key" not in st.session_state:
            st.session_state.vt_api_key = None
        
        st.divider()
        
        # Settings
        st.subheader("Tùy chọn quét")
        static_only = st.checkbox("Chỉ quét tĩnh", value=False)
        dynamic_only = st.checkbox("Chỉ quét động", value=False)
        include_threat_intel = st.checkbox("Bao gồm Threat Intelligence", value=True)
        timeout = st.slider("Timeout (giây)", min_value=1, max_value=60, value=5)
        
        st.divider()
        
        # Info
        st.info("""
        **VeriModel** bảo vệ bạn khỏi các cuộc tấn công qua file pickle:
        - 🚨 Remote Code Execution (RCE)
        - 🌐 Data Exfiltration
        - 💣 Backdoor Installation
        
        Hỗ trợ: `.pkl`, `.pickle`, `.pth`
        """)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Quét File", "🔄 Chuyển đổi", "📊 Threat Intelligence", "ℹ️ Thông tin"])

    with tab1:
        scan_tab(static_only, dynamic_only, include_threat_intel, timeout)

    with tab2:
        convert_tab()

    with tab3:
        threat_intel_tab()

    with tab4:
        info_tab()


def scan_tab(static_only: bool, dynamic_only: bool, include_threat_intel: bool, timeout: int):
    """Tab quét file."""
    st.header("Quét File để Phát hiện Mã độc hại")
    
    uploaded_file = st.file_uploader(
        "Chọn file cần quét",
        type=["pkl", "pickle", "pth"],
        help="Hỗ trợ các định dạng: .pkl, .pickle, .pth"
    )
    
    if uploaded_file is not None:
        # Hiển thị thông tin file
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tên file", uploaded_file.name)
        with col2:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.metric("Kích thước", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("Loại file", uploaded_file.type or "Unknown")
        
        # Button quét
        if st.button("🔍 Bắt đầu Quét", type="primary", use_container_width=True):
            with st.spinner("Đang quét file..."):
                # Lưu file tạm thời
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = Path(tmp_file.name)
                
                results = {}
                
                # Static scan
                if not dynamic_only:
                    with st.expander("📊 Quét Tĩnh", expanded=True):
                        static_result = st.session_state.scanner.scan_file(tmp_path)
                        results["static"] = static_result
                        display_static_results(static_result)
                
                # Dynamic scan
                if not static_only:
                    with st.expander("🔬 Quét Động", expanded=True):
                        if st.session_state.dynamic_scanner.is_supported():
                            with st.spinner("Đang thực thi trong sandbox..."):
                                dynamic_result = st.session_state.dynamic_scanner.scan(str(tmp_path), timeout=timeout)
                                results["dynamic"] = dynamic_result
                                display_dynamic_results(dynamic_result)
                        else:
                            st.warning("⚠️ Quét động yêu cầu Docker đang chạy.")
                            results["dynamic"] = {"error": "Docker not available"}
                
                # Threat Intelligence
                if include_threat_intel:
                    with st.expander("🕵️ Threat Intelligence", expanded=True):
                        with st.spinner("Đang tra cứu Threat Intelligence..."):
                            ti_result = st.session_state.threat_intel.analyze_file(
                                tmp_path, 
                                check_vt=bool(st.session_state.get("vt_api_key"))
                            )
                            results["threat_intelligence"] = ti_result
                            display_threat_intel_results(ti_result)
                
                # Final verdict
                st.divider()
                display_final_verdict(results)
                
                # Cleanup
                if tmp_path.exists():
                    os.unlink(tmp_path)


def display_static_results(result: dict):
    """Hiển thị kết quả quét tĩnh."""
    if result.get("error"):
        st.error(f"❌ Lỗi: {result['error']}")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng Opcodes", result.get("total_opcodes", 0))
    with col2:
        threats_count = len(result.get("threats", []))
        st.metric("Mối đe dọa", threats_count, delta=None if threats_count == 0 else f"+{threats_count}")
    with col3:
        warnings_count = len(result.get("warnings", []))
        st.metric("Cảnh báo", warnings_count, delta=None if warnings_count == 0 else f"+{warnings_count}")
    
    # Threats
    threats = result.get("threats", [])
    if threats:
        st.subheader("🚨 Mối đe dọa phát hiện:")
        for threat in threats:
            severity_color = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }.get(threat.get("severity", "MEDIUM"), "⚪")
            
            st.markdown(f"""
            **{severity_color} {threat.get('type', 'Unknown')}** ({threat.get('severity', 'MEDIUM')})
            - {threat.get('description', 'No description')}
            """)
    
    # Warnings
    warnings = result.get("warnings", [])
    if warnings:
        st.subheader("⚠️ Cảnh báo:")
        for warning in warnings:
            st.info(f"**{warning.get('type')}**: {warning.get('description')}")


def display_dynamic_results(result: dict):
    """Hiển thị kết quả quét động."""
    if result.get("error"):
        st.error(f"❌ Lỗi: {result['error']}")
        return
    
    threats = result.get("threats", [])
    is_safe = result.get("is_safe", True)
    
    if is_safe:
        st.success("✅ Không phát hiện hành vi độc hại trong sandbox")
    else:
        st.error(f"🚨 Phát hiện {len(threats)} hành vi độc hại")
    
    if threats:
        for threat in threats:
            st.markdown(f"""
            **{threat.get('type')}** ({threat.get('severity', 'MEDIUM')})
            - {threat.get('description')}
            """)


def display_threat_intel_results(result: dict):
    """Hiển thị kết quả Threat Intelligence."""
    if result.get("error"):
        st.error(f"❌ Lỗi: {result['error']}")
        return
    
    iocs = result.get("iocs", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hashes phát hiện", len(iocs.get("hashes", [])))
    with col2:
        st.metric("IPs phát hiện", len(iocs.get("ips", [])))
    with col3:
        st.metric("Domains phát hiện", len(iocs.get("domains", [])))
    
    # IOCs
    if iocs.get("hashes"):
        with st.expander("📋 Hashes"):
            for h in iocs["hashes"][:10]:  # Limit display
                st.code(h[:64] + "..." if len(h) > 64 else h)
    
    if iocs.get("ips"):
        with st.expander("🌐 IP Addresses"):
            st.write(iocs["ips"])
    
    if iocs.get("domains"):
        with st.expander("🔗 Domains"):
            st.write(iocs["domains"])
    
    # VirusTotal results
    vt_results = result.get("virustotal_results", {})
    if vt_results:
        st.subheader("🕵️ VirusTotal Results")
        st.json(vt_results)
    
    # Threats từ TI
    threats = result.get("threats", [])
    if threats:
        st.subheader("🚨 Threat Intelligence Alerts")
        for threat in threats:
            st.error(f"**{threat.get('type')}**: {threat.get('description')}")
    
    warnings = result.get("warnings", [])
    if warnings:
        for warning in warnings:
            st.warning(f"**{warning.get('type')}**: {warning.get('description')}")


def display_final_verdict(results: dict):
    """Hiển thị kết luận cuối cùng."""
    is_safe = True
    reasons = []
    
    if results.get("static") and not results["static"].get("error"):
        if not results["static"].get("is_safe", True):
            is_safe = False
            reasons.append(f"Quét tĩnh: {len(results['static'].get('threats', []))} mối đe dọa")
    
    if results.get("dynamic") and not results["dynamic"].get("error"):
        if results["dynamic"].get("is_safe") is False:
            is_safe = False
            reasons.append(f"Quét động: {len(results['dynamic'].get('threats', []))} hành vi nguy hiểm")
    
    if results.get("threat_intelligence") and results["threat_intelligence"].get("threats"):
        is_safe = False
        reasons.append(f"Threat Intelligence: {len(results['threat_intelligence']['threats'])} mối đe dọa")
    
    # Display verdict
    if is_safe:
        st.success("""
        ## ✅ KẾT LUẬN: FILE AN TOÀN
        
        Không phát hiện mã độc hại hoặc hành vi nguy hiểm.
        """)
    else:
        st.error("""
        ## 🚨 KẾT LUẬN: FILE NGUY HIỂM
        
        **Lý do:**
        """)
        for reason in reasons:
            st.markdown(f"- {reason}")
        
        st.warning("""
        **⚠️ KHUYẾN NGHỊ:**
        - ❌ KHÔNG tải (load) file này vào môi trường production
        - 🔍 Xem xét nguồn gốc của file
        - 🔄 Sử dụng định dạng an toàn hơn như .safetensors
        """)


def convert_tab():
    """Tab chuyển đổi sang safetensors."""
    st.header("Chuyển đổi sang Safetensors")
    
    if not st.session_state.converter.is_supported():
        st.error("⚠️ Safetensors converter không được hỗ trợ. Vui lòng cài đặt PyTorch và safetensors.")
        st.code("pip install torch safetensors")
        return
    
    uploaded_file = st.file_uploader(
        "Chọn file cần chuyển đổi",
        type=["pkl", "pickle", "pth"],
        help="Chỉ chuyển đổi các file đã được verified an toàn!"
    )
    
    safe_mode = st.checkbox(
        "Safe Mode (cảnh báo khi load pickle)",
        value=True,
        help="Hiển thị cảnh báo khi load file pickle"
    )
    
    if uploaded_file is not None:
        if st.button("🔄 Chuyển đổi", type="primary", use_container_width=True):
            with st.spinner("Đang chuyển đổi..."):
                # Lưu file tạm thời
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = Path(tmp_file.name)
                
                output_path = tmp_path.with_suffix('.safetensors')
                
                # Chuyển đổi
                if tmp_path.suffix.lower() in ['.pkl', '.pickle']:
                    result = st.session_state.converter.convert_pickle_to_safetensors(
                        tmp_path, output_path, safe_mode=safe_mode
                    )
                elif tmp_path.suffix.lower() == '.pth':
                    result = st.session_state.converter.convert_pytorch_to_safetensors(
                        tmp_path, output_path
                    )
                else:
                    st.error(f"Định dạng không được hỗ trợ: {tmp_path.suffix}")
                    return
                
                if result.get("success"):
                    st.success(f"✅ {result.get('message')}")
                    
                    # Download button
                    if output_path.exists():
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label="📥 Tải file .safetensors",
                                data=f.read(),
                                file_name=output_path.name,
                                mime="application/octet-stream",
                                use_container_width=True
                            )
                    
                    # Info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Số tensors", result.get("tensors_count", 0))
                    with col2:
                        st.metric("Metadata keys", result.get("metadata_keys", 0))
                else:
                    st.error(f"❌ Lỗi: {result.get('error')}")
                
                # Cleanup
                if tmp_path.exists():
                    os.unlink(tmp_path)


def threat_intel_tab():
    """Tab Threat Intelligence."""
    st.header("Threat Intelligence Query")
    
    query_type = st.radio(
        "Loại truy vấn",
        ["Hash", "IP Address", "Domain", "File Analysis"],
        horizontal=True
    )
    
    if query_type == "Hash":
        hash_value = st.text_input("Nhập hash (MD5, SHA1, hoặc SHA256)")
        if st.button("🔍 Tra cứu", type="primary"):
            if hash_value:
                result = st.session_state.threat_intel.query_virustotal_hash(hash_value)
                if result:
                    st.json(result)
                    if result.get("found") and result.get("positives", 0) > 0:
                        st.error(f"⚠️ Hash được phát hiện bởi {result['positives']}/{result['total']} antivirus engines")
                else:
                    st.warning("Không có kết quả hoặc không có API key")
    
    elif query_type == "IP Address":
        ip = st.text_input("Nhập IP address")
        if st.button("🔍 Tra cứu", type="primary"):
            if ip:
                result = st.session_state.threat_intel.query_virustotal_ip(ip)
                if result:
                    st.json(result)
                    if result.get("found") and result.get("detected_urls"):
                        st.warning(f"⚠️ IP có liên quan đến {len(result['detected_urls'])} URL độc hại")
                else:
                    st.warning("Không có kết quả hoặc không có API key")
    
    elif query_type == "Domain":
        domain = st.text_input("Nhập domain")
        if st.button("🔍 Tra cứu", type="primary"):
            if domain:
                result = st.session_state.threat_intel.query_virustotal_domain(domain)
                if result:
                    st.json(result)
                    if result.get("found") and result.get("detected_urls"):
                        st.warning(f"⚠️ Domain có liên quan đến {len(result['detected_urls'])} URL độc hại")
                else:
                    st.warning("Không có kết quả hoặc không có API key")
    
    elif query_type == "File Analysis":
        uploaded_file = st.file_uploader("Chọn file để phân tích IOCs", type=["pkl", "pickle", "pth"])
        if uploaded_file and st.button("🔍 Phân tích", type="primary"):
            with st.spinner("Đang phân tích..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = Path(tmp_file.name)
                
                result = st.session_state.threat_intel.analyze_file(tmp_path, check_vt=True)
                display_threat_intel_results(result)
                
                if tmp_path.exists():
                    os.unlink(tmp_path)


def info_tab():
    """Tab thông tin."""
    st.header("Thông tin về VeriModel")
    
    st.markdown("""
    ## 🛡️ VeriModel - AI Supply Chain Firewall
    
    **VeriModel** là một công cụ bảo mật được thiết kế để quét và phát hiện mã độc hại 
    trong các file mô hình AI dựa trên pickle.
    
    ### ✨ Tính năng
    
    - **Quét Tĩnh**: Phân tích bytecode pickle mà không thực thi
    - **Quét Động**: Thực thi mô hình trong Docker sandbox
    - **Threat Intelligence**: Tra cứu hash/IP/domain trên VirusTotal
    - **Safetensors Converter**: Chuyển đổi sang định dạng an toàn
    
    ### 📋 Hỗ trợ Định dạng
    
    - `.pkl`, `.pickle` - Python pickle files
    - `.pth` - PyTorch checkpoint files
    
    ### 🔧 Yêu cầu
    
    - Python 3.10+
    - Docker (cho quét động)
    - VirusTotal API Key (cho Threat Intelligence, tùy chọn)
    
    ### 📚 Tài liệu
    
    Xem [README.md](../README.md) để biết thêm chi tiết.
    """)


if __name__ == "__main__":
    main()

