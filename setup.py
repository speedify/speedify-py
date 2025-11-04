"""
Minimal setup.py for compatibility.
All configuration is in pyproject.toml.
extras_require is duplicated here for compatibility with older pip/setuptools.
"""
from setuptools import setup

setup(
    extras_require={
        "test": [
            "pytest>=7.0",
            "pytest-mock>=3.10",
            "pytest-cov>=4.0",
        ],
    },
)
