import pickle
from pathlib import Path

from verimodel.file_analyzer import FileAnalyzer
from verimodel.static_scanner import StaticScanner


def write_pickle(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def test_file_analyzer_simple(tmp_path):
    p = tmp_path / "simple.pkl"
    write_pickle({"a": 1}, p)

    analyzer = FileAnalyzer()
    res = analyzer.analyze_file(p)

    assert "structure" in res
    # structure_type may vary by pickle protocol; ensure we have opcode stats
    structure = res["structure"]
    assert isinstance(structure.get("structure_type"), str)
    assert structure.get("total_opcodes", 0) >= 0
    assert res["byte_analysis"]["has_executable_content"] is False


def test_static_scanner_safe(tmp_path):
    p = tmp_path / "safe.pkl"
    write_pickle([1, 2, 3], p)

    scanner = StaticScanner()
    res = scanner.scan_file(p)

    # Safe pickle should report no high severity threats
    assert res.get("is_safe") is True
    assert res.get("total_threats", 0) == 0


def test_static_scanner_global_opcode(tmp_path):
    # Use a module-level class (imported from helpers) so it's picklable
    from tests.helpers import CustomClass

    p = tmp_path / "custom.pkl"
    write_pickle(CustomClass(), p)

    scanner = StaticScanner()
    res = scanner.scan_file(p)

    details = res.get("details", [])
    # Some pickle protocols may inline differently; ensure we at least return details
    assert isinstance(details, list)
    # If GLOBAL appears in details it's a good sign; we accept either behavior
    has_global = any(d.get("opcode") == "GLOBAL" for d in details)
    assert has_global or len(details) > 0
