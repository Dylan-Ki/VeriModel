# Demo Models

This folder contains safe demo artifacts and a small generator script for
testing the VeriModel scanners.

Files
- `generate_demo_models.py` - script to create demo files. By default it creates
  safe, non-destructive examples. To create a demo pickle that executes a
  command when unpickled you MUST pass `--dangerous` and set the environment
  variable `ALLOW_DANGEROUS=1`.

Usage

Create safe demos:

```bash
python demo_models/generate_demo_models.py --outdir demo_models
```

Create dangerous demo (explicit opt-in):

```bash
# Unix / PowerShell: set env var and run
export ALLOW_DANGEROUS=1
python demo_models/generate_demo_models.py --dangerous --outdir demo_models
```

Safety notes
- The "dangerous" demo will execute a shell command when unpickled. We only
  create a harmless marker file (`dangerous_demo.marker`) for demonstration.
- Do NOT unpickle files from untrusted sources on production systems.

Instructor notes
- Use the safe demo for classroom exercises. If you want to demonstrate
  execution behavior, use the dangerous demo only in an isolated environment
  (e.g., a disposable VM or container).
