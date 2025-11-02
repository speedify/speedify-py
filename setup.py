"""
Setup script for speedify-py
"""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="speedify-py",
    version="16.0.2",
    author="Speedify Team",
    description="Python library to control Speedify bonding VPN via CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/speedify/speedify-py",
    project_urls={
        "Documentation": "https://support.speedify.com/article/285-speedify-command-line-interface",
        "Source": "https://github.com/speedify/speedify-py",
    },
    py_modules=["speedify", "speedifysettings", "speedifyutil", "utils"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.7",
    keywords="speedify vpn bonding cli networking",
)