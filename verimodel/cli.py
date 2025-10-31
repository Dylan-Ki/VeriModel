"""
CLI Module

Command-line interface for VeriModel using Typer and Rich.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from typing import Optional

from verimodel import __version__
from verimodel.static_scanner import StaticScanner
from verimodel.dynamic_scanner import DynamicScanner

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

    # ============ KẾT LUẬN TỔNG THỂ ============
    _display_final_verdict(results)


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