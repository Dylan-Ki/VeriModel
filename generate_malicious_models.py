"""
Top-level placeholder for demo generator.

For safety, demo generators are now located in the `demo_models/` folder.
Run `python demo_models/generate_demo_models.py --help` for usage. By default
the script only creates non-destructive demo files. To create a file that will
execute a command when unpickled you must explicitly pass `--dangerous` and
set the environment variable `ALLOW_DANGEROUS=1` to acknowledge the risk.

This top-level file is kept as a pointer to the safe demo scripts.
"""

import sys

def main():
    print("Demo generator moved to demo_models/generate_demo_models.py")
    print("Run: python demo_models/generate_demo_models.py --help")

if __name__ == '__main__':
    main()
