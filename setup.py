"""
Minimal setup.py for backward compatibility with editable installs.
Most configuration is in pyproject.toml.
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
