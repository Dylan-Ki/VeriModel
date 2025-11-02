"""
CLI Module

Command-line interface for VeriModel using Typer and Rich.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Optional

from verimodel import __version__
from verimodel.static_scanner import StaticScanner
from verimodel.dynamic_scanner import DynamicScanner
from verimodel.threat_intelligence import ThreatIntelligence
from verimodel.safetensors_converter import SafetensorsConverter
import os

app = typer.Typer(
    name="verimodel",
    help="🛡️  VeriModel - AI Supply Chain Firewall\n\nScan pickle-based ML models for malicious code.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """Hiển thị phiên bản."""
    if value:
        console.print(f"[bold cyan]VeriModel[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.command()
def scan(
    file_path: Path = typer.Argument(..., help="Đường dẫn đến file .pkl cần quét"),
    static_only: bool = typer.Option(
        False, "--static-only", "-s", help="Chỉ chạy quét tĩnh (bỏ qua quét động)"
    ),
    dynamic_only: bool = typer.Option(
        False, "--dynamic-only", "-d", help="Chỉ chạy quét động (bỏ qua quét tĩnh)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Hiển thị chi tiết đầy đủ"),
    timeout: int = typer.Option(
        5, "--timeout", "-t", help="Timeout cho quét động (giây)", min=1, max=60
    ),
    threat_intel: bool = typer.Option(
        False, "--threat-intel", "-ti", help="Bao gồm Threat Intelligence (yêu cầu VIRUSTOTAL_API_KEY)"
    ),
):
    """
    🔍 Quét file pickle để phát hiện mã độc hại.

    Mặc định sẽ chạy cả quét tĩnh và quét động (nếu hệ thống hỗ trợ).
    """
    file_path = Path(file_path)

    # Header
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]🛡️  VeriModel Scanner[/bold cyan]\n"
            f"[dim]Scanning:[/dim] [yellow]{file_path.name}[/yellow]",
            border_style="cyan",
        )
    )
    console.print()

    results = {}

    # ============ QUÉT TĨNH ============
    if not dynamic_only:
        console.print("[bold blue]📊 Đang chạy quét tĩnh...[/bold blue]")
        static_scanner = StaticScanner()
        static_result = static_scanner.scan_file(file_path)
        results["static"] = static_result

        # Hiển thị kết quả quét tĩnh
        _display_static_results(static_result, verbose)
        console.print()

    # ============ QUÉT ĐỘNG ============
    if not static_only:
        console.print("[bold blue]🔬 Đang chạy quét động...[/bold blue]")
        dynamic_scanner = DynamicScanner()

        if not dynamic_scanner.is_supported():
            console.print(
                "[yellow]⚠️  Quét động chỉ hỗ trợ trên Linux. "
                "Hệ điều hành hiện tại không được hỗ trợ.[/yellow]"
            )
        else:
            with console.status("[bold green]Đang thực thi model trong sandbox..."):
                dynamic_result = dynamic_scanner.scan(str(file_path), timeout=timeout)
            results["dynamic"] = dynamic_result

            # Hiển thị kết quả quét động
            _display_dynamic_results(dynamic_result, verbose)
            console.print()

    # ============ THREAT INTELLIGENCE ============
    if threat_intel:
        console.print("[bold blue]🕵️  Đang tra cứu Threat Intelligence...[/bold blue]")
        threat_intel_scanner = ThreatIntelligence()
        ti_result = threat_intel_scanner.analyze_file(file_path, check_vt=True)
        results["threat_intelligence"] = ti_result
        
        _display_threat_intel_results(ti_result, verbose)
        console.print()

    # ============ KẾT LUẬN TỔNG THỂ ============
    _display_final_verdict(results)


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Đường dẫn đến file cần chuyển đổi"),
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Đường dẫn file output (mặc định: cùng tên với .safetensors)"
    ),
    safe_mode: bool = typer.Option(
        True, "--safe-mode/--no-safe-mode", help="Safe mode (cảnh báo khi load pickle)"
    ),
):
    """
    🔄 Chuyển đổi file model sang định dạng safetensors an toàn.
    
    CHÚ Ý: Chỉ sử dụng với các file đã được verified an toàn!
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        console.print(f"[red]❌ File không tồn tại: {input_path}[/red]")
        raise typer.Exit(code=1)
    
    converter = SafetensorsConverter()
    
    if not converter.is_supported():
        console.print("[red]❌ Safetensors converter không được hỗ trợ.[/red]")
        console.print("[yellow]Vui lòng cài đặt: pip install torch safetensors[/yellow]")
        raise typer.Exit(code=1)
    
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]🔄 Safetensors Converter[/bold cyan]\n"
            f"[dim]Converting:[/dim] [yellow]{input_path.name}[/yellow]",
            border_style="cyan",
        )
    )
    console.print()
    
    if input_path.suffix.lower() in ['.pkl', '.pickle']:
        result = converter.convert_pickle_to_safetensors(input_path, output_path, safe_mode=safe_mode)
    elif input_path.suffix.lower() == '.pth':
        result = converter.convert_pytorch_to_safetensors(input_path, output_path)
    else:
        console.print(f"[red]❌ Định dạng không được hỗ trợ: {input_path.suffix}[/red]")
        raise typer.Exit(code=1)
    
    if result.get("success"):
        console.print(f"[green]✅ {result.get('message')}[/green]")
        console.print(f"[dim]Output: {result['output_path']}[/dim]")
    else:
        console.print(f"[red]❌ Lỗi: {result.get('error')}[/red]")
        raise typer.Exit(code=1)


@app.command()
def threat_intel(
    file_path: Optional[Path] = typer.Option(None, "--file", "-f", help="Đường dẫn file để phân tích"),
    file_hash: Optional[str] = typer.Option(None, "--hash", help="Hash để tra cứu (MD5, SHA1, SHA256)"),
    ip: Optional[str] = typer.Option(None, "--ip", help="IP address để tra cứu"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain để tra cứu"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Hiển thị chi tiết đầy đủ"),
):
    """
    🕵️  Tra cứu Threat Intelligence từ VirusTotal.
    
    Yêu cầu: VIRUSTOTAL_API_KEY environment variable.
    """
    ti = ThreatIntelligence()
    
    if not ti.vt_api_key:
        console.print("[yellow]⚠️  Không có VirusTotal API key.[/yellow]")
        console.print("[dim]Đặt VIRUSTOTAL_API_KEY environment variable để sử dụng tính năng này.[/dim]")
        console.print()
        if not any([file_path, file_hash, ip, domain]):
            raise typer.Exit(code=1)
    
    console.print()
    console.print(Panel.fit("[bold cyan]🕵️  Threat Intelligence Query[/bold cyan]", border_style="cyan"))
    console.print()
    
    # Query hash
    if file_hash:
        console.print(f"[blue]Đang tra cứu hash: {file_hash[:16]}...[/blue]")
        result = ti.query_virustotal_hash(file_hash)
        if result:
            if result.get("found") and result.get("positives", 0) > 0:
                console.print(f"[red]🚨 Hash được phát hiện bởi {result['positives']}/{result['total']} engines[/red]")
                if result.get("permalink"):
                    console.print(f"[dim]Link: {result['permalink']}[/dim]")
            else:
                console.print("[green]✅ Hash không được phát hiện trong VirusTotal database[/green]")
        console.print()
    
    # Query IP
    if ip:
        console.print(f"[blue]Đang tra cứu IP: {ip}[/blue]")
        result = ti.query_virustotal_ip(ip)
        if result:
            if result.get("found"):
                detected = len(result.get("detected_urls", []))
                if detected > 0:
                    console.print(f"[red]🚨 IP có liên quan đến {detected} URL độc hại[/red]")
                else:
                    console.print("[green]✅ IP không có lịch sử độc hại[/green]")
        console.print()
    
    # Query domain
    if domain:
        console.print(f"[blue]Đang tra cứu domain: {domain}[/blue]")
        result = ti.query_virustotal_domain(domain)
        if result:
            if result.get("found"):
                detected = len(result.get("detected_urls", []))
                if detected > 0:
                    console.print(f"[red]🚨 Domain có liên quan đến {detected} URL độc hại[/red]")
                else:
                    console.print("[green]✅ Domain không có lịch sử độc hại[/green]")
        console.print()
    
    # Analyze file
    if file_path:
        file_path = Path(file_path)
        if not file_path.exists():
            console.print(f"[red]❌ File không tồn tại: {file_path}[/red]")
            raise typer.Exit(code=1)
        
        console.print(f"[blue]Đang phân tích file: {file_path.name}[/blue]")
        result = ti.analyze_file(file_path, check_vt=True)
        _display_threat_intel_results(result, verbose)


@app.command()
def info(
    file_path: Path = typer.Argument(..., help="Đường dẫn đến file .pkl"),
):
    """
    ℹ️  Hiển thị thông tin cơ bản về file pickle.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        console.print(f"[red]❌ File không tồn tại: {file_path}[/red]")
        raise typer.Exit(code=1)

    # Thu thập thông tin
    file_size = file_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    # Hiển thị
    info_table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="yellow")

    info_table.add_row("📁 Tên file", file_path.name)
    info_table.add_row("📂 Thư mục", str(file_path.parent))
    info_table.add_row("📊 Kích thước", f"{file_size:,} bytes ({file_size_mb:.2f} MB)")
    info_table.add_row("🏷️  Định dạng", file_path.suffix)

    console.print()
    console.print(Panel(info_table, title="[bold cyan]File Information[/bold cyan]"))
    console.print()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Hiển thị phiên bản"
    ),
):
    """
    🛡️  VeriModel - AI Supply Chain Firewall

    Công cụ bảo mật để quét các file mô hình AI (pickle-based) nhằm phát hiện mã độc hại.
    """
    pass


def _display_static_results(result: dict, verbose: bool):
    """Hiển thị kết quả quét tĩnh."""
    if result.get("error"):
        console.print(f"[red]❌ {result['error']}[/red]")
        return

    threats = result.get("threats", [])
    warnings = result.get("warnings", [])
    total_opcodes = result.get("total_opcodes", 0)

    # Bảng tóm tắt
    summary_table = Table(show_header=False, box=box.SIMPLE)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value")

    summary_table.add_row("Tổng số opcodes", str(total_opcodes))
    summary_table.add_row("Mối đe dọa", f"[red]{len(threats)}[/red]" if threats else "[green]0[/green]")
    summary_table.add_row(
        "Cảnh báo", f"[yellow]{len(warnings)}[/yellow]" if warnings else "[green]0[/green]"
    )

    console.print(summary_table)

    # Hiển thị mối đe dọa
    if threats:
        console.print("\n[bold red]🚨 Mối đe dọa phát hiện:[/bold red]")
        for i, threat in enumerate(threats, 1):
            console.print(
                f"  {i}. [red]{threat['type']}[/red] (Mức độ: {threat['severity']})"
            )
            console.print(f"     → {threat['description']}")
            if verbose and threat.get("argument"):
                console.print(f"     [dim]Argument: {threat['argument']}[/dim]")

    # Hiển thị cảnh báo
    if warnings and verbose:
        console.print("\n[bold yellow]⚠️  Cảnh báo:[/bold yellow]")
        for i, warning in enumerate(warnings, 1):
            console.print(
                f"  {i}. [yellow]{warning['type']}[/yellow] (Mức độ: {warning['severity']})"
            )
            console.print(f"     → {warning['description']}")


def _display_dynamic_results(result: dict, verbose: bool):
    """Hiển thị kết quả quét động."""
    if result.get("error"):
        console.print(f"[red]❌ {result['error']}[/red]")
        return

    threats = result.get("threats", [])
    syscalls = result.get("syscalls", [])

    # Bảng tóm tắt
    summary_table = Table(show_header=False, box=box.SIMPLE)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value")

    summary_table.add_row("Tổng syscalls giám sát", str(len(syscalls)))
    summary_table.add_row(
        "Mối đe dọa", f"[red]{len(threats)}[/red]" if threats else "[green]0[/green]"
    )

    console.print(summary_table)

    # Hiển thị mối đe dọa
    if threats:
        console.print("\n[bold red]🚨 Hành vi độc hại phát hiện:[/bold red]")
        for i, threat in enumerate(threats, 1):
            console.print(
                f"  {i}. [red]{threat['type']}[/red] (Mức độ: {threat['severity']})"
            )
            console.print(f"     → {threat['description']}")
            if verbose and threat.get("details"):
                console.print(f"     [dim]{threat['details'][:100]}...[/dim]")

    # Hiển thị syscalls
    if syscalls and verbose:
        console.print(f"\n[dim]Syscalls được ghi nhận: {len(syscalls)} lệnh[/dim]")


def _display_threat_intel_results(result: dict, verbose: bool):
    """Hiển thị kết quả Threat Intelligence."""
    if result.get("error"):
        console.print(f"[red]❌ Lỗi: {result['error']}[/red]")
        return
    
    iocs = result.get("iocs", {})
    
    # Tóm tắt IOCs
    summary_table = Table(show_header=False, box=box.SIMPLE)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value")
    
    summary_table.add_row("Hashes phát hiện", str(len(iocs.get("hashes", []))))
    summary_table.add_row("IPs phát hiện", str(len(iocs.get("ips", []))))
    summary_table.add_row("Domains phát hiện", str(len(iocs.get("domains", []))))
    
    console.print(summary_table)
    
    # Threats từ TI
    threats = result.get("threats", [])
    if threats:
        console.print("\n[bold red]🚨 Threat Intelligence Alerts:[/bold red]")
        for i, threat in enumerate(threats, 1):
            console.print(
                f"  {i}. [red]{threat['type']}[/red] ({threat.get('severity', 'MEDIUM')})"
            )
            console.print(f"     → {threat['description']}")
            if verbose and threat.get("virustotal_permalink"):
                console.print(f"     [dim]Link: {threat['virustotal_permalink']}[/dim]")
    
    # Warnings
    warnings = result.get("warnings", [])
    if warnings:
        console.print("\n[bold yellow]⚠️  Cảnh báo:[/bold yellow]")
        for i, warning in enumerate(warnings, 1):
            console.print(
                f"  {i}. [yellow]{warning['type']}[/yellow] ({warning.get('severity', 'LOW')})"
            )
            console.print(f"     → {warning['description']}")
    
    # IOCs chi tiết (nếu verbose)
    if verbose:
        if iocs.get("hashes"):
            console.print("\n[dim]Hashes:[/dim]")
            for h in iocs["hashes"][:5]:  # Limit
                console.print(f"  [dim]{h[:32]}...[/dim]" if len(h) > 32 else f"  [dim]{h}[/dim]")
        if iocs.get("ips"):
            console.print(f"\n[dim]IPs: {', '.join(iocs['ips'][:5])}[/dim]")
        if iocs.get("domains"):
            console.print(f"\n[dim]Domains: {', '.join(iocs['domains'][:5])}[/dim]")


def _display_final_verdict(results: dict):
    """Hiển thị kết luận cuối cùng."""
    static_result = results.get("static")
    dynamic_result = results.get("dynamic")

    # Tính toán verdict tổng thể
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

    ti_result = results.get("threat_intelligence")
    if ti_result and not ti_result.get("error"):
        if ti_result.get("threats"):
            is_safe = False
            reasons.append(f"Threat Intelligence phát hiện {len(ti_result['threats'])} mối đe dọa")

    # Hiển thị verdict
    console.print("=" * 70)
    if is_safe:
        verdict_text = "✅ KẾT LUẬN: FILE AN TOÀN"
        verdict_style = "bold green"
        verdict_desc = "Không phát hiện mã độc hại hoặc hành vi nguy hiểm."
    else:
        verdict_text = "🚨 KẾT LUẬN: FILE NGUY HIỂM"
        verdict_style = "bold red"
        verdict_desc = "\n".join([f"  • {reason}" for reason in reasons])

    console.print(
        Panel(
            f"[{verdict_style}]{verdict_text}[/{verdict_style}]\n\n{verdict_desc}",
            border_style="red" if not is_safe else "green",
            box=box.DOUBLE,
        )
    )
    console.print()

    # Khuyến nghị
    if not is_safe:
        console.print("[bold yellow]⚠️  KHUYẾN NGHỊ:[/bold yellow]")
        console.print("  • KHÔNG tải (load) file này vào môi trường production")
        console.print("  • Xem xét nguồn gốc của file")
        console.print("  • Sử dụng định dạng an toàn hơn như .safetensors")
        console.print()


if __name__ == "__main__":
    app()