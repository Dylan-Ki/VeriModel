#!/usr/bin/env python3
"""
Demo model generator (safe by default).

Creates non-destructive demo pickle and PyTorch state files for testing the
VeriModel scanners. Creating pickles that execute code when unpickled is
potentially dangerous; this script requires an explicit `--dangerous` flag and
the environment variable `ALLOW_DANGEROUS=1` to produce such files.
"""
import argparse
import os
import pickle
from pathlib import Path

try:
    import torch
except Exception:
    torch = None


def write_safe_pickle(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"type": "safe_demo", "note": "This is a safe demo pickle."}
    with open(path, "wb") as f:
        pickle.dump(data, f)
    print(f"Wrote safe demo pickle: {path}")


def write_safe_torch(path: Path):
    if torch is None:
        print("PyTorch not available; skipping torch demo file")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    # simple state dict
    model_state = {"weights": [1.0, 2.0, 3.0], "meta": "safe demo"}
    torch.save(model_state, path)
    print(f"Wrote safe torch state file: {path}")


def write_dangerous_pickle(path: Path):
    """Create a pickle that will execute a harmless shell command when loaded.

    WARNING: Only create this if the user explicitly opts in and sets
    environment variable ALLOW_DANGEROUS=1. The command executed is a harmless
    echo that writes a marker file inside the demo_models folder.
    """
    class Marker:
        def __reduce__(self):
            cmd = f'echo "MALICIOUS_MARKER" > "{path.with_suffix(".marker")}"'
            return os.system, (cmd,)

    with open(path, "wb") as f:
        pickle.dump(Marker(), f)
    print(f"Wrote DANGEROUS demo pickle (will execute on load): {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate demo model files (safe by default)")
    parser.add_argument("--dangerous", action="store_true", help="Create demo files that execute code when unpickled (requires ALLOW_DANGEROUS=1)")
    parser.add_argument("--outdir", default=".", help="Output directory for demos")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    safe_pkl = outdir / "safe_demo.pkl"
    write_safe_pickle(safe_pkl)

    safe_torch = outdir / "safe_torch.pth"
    write_safe_torch(safe_torch)

    if args.dangerous:
        if os.environ.get("ALLOW_DANGEROUS") != "1":
            print("Refusing to create dangerous demo: set ALLOW_DANGEROUS=1 in the environment to acknowledge risk.")
            return
        dangerous_pkl = outdir / "dangerous_demo.pkl"
        write_dangerous_pickle(dangerous_pkl)


if __name__ == "__main__":
    main()
