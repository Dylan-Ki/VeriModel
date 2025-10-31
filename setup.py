from setuptools import setup, find_packages

setup(
    name="verimodel",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "rich",
        "tkinter"
    ],
    entry_points={
        'console_scripts': [
            'verimodel-gui=verimodel.gui:main',
        ],
    },
    author="Dylan-Ki",
    description="AI Supply Chain Firewall - Quét và phân tích mô hình AI để phát hiện mã độc",
    long_description=open("verimodel/README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dylan-Ki/VeriModel",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)