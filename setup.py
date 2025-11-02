"""
Setup configuration for VeriModel.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __init__.py
init_file = Path(__file__).parent / "verimodel" / "__init__.py"
version = "0.2.0"
if init_file.exists():
    for line in init_file.read_text().splitlines():
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="verimodel",
    version=version,
    packages=find_packages(exclude=["tests", "test_models", "demo_models", "*.tests", "*.tests.*"]),
    install_requires=[
        # Core web dependencies
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.0",
        "python-multipart>=0.0.6",
        # CLI dependencies
        "rich>=10.0.0",
        "typer>=0.9.0",
        # Scanner dependencies
        "yara-python>=4.5.0",
        "docker>=7.0.0",
        # Threat Intelligence
        "requests>=2.31.0",
        # Safetensors (optional but recommended)
        "safetensors>=0.4.0",
    ],
    extras_require={
        "torch": ["torch>=2.0.0"],  # Optional PyTorch for converter
        "dev": [
            "pytest>=7.4.3",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "pip-audit>=2.7.3",
        ],
    },
    entry_points={
        'console_scripts': [
            'verimodel=verimodel.cli:app',
            'verimodel-gui=verimodel.gui:main',
        ],
    },
    author="Tran Tuan Anh (Dylan-Ki)",
    author_email="dyltran3@gmail.com",
    description="AI Supply Chain Firewall - Scan and detect malicious code in pickle-based ML models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dylan-Ki/VeriModel",
    license="MIT",
    keywords=["security", "ai", "ml", "pickle", "model", "firewall", "scanner", "yara", "sandbox"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    package_data={
        "verimodel": [
            "rules/*.yar",
        ],
    },
)