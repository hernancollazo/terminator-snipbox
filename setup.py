#!/usr/bin/env python3
"""
Setup script for SnipBox Terminator Plugin

Install with: pip install -e .
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snipbox",
    version="1.0.0",
    author="Hernán Collazo",
    description="SnipBox - A snippet manager plugin for Terminator terminal multiplexer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hernancollazo/terminator-snipbox",
    license="MIT",
    py_modules=["snipbox"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Shells",
    ],
    python_requires=">=3.6",
    project_urls={
        "Bug Reports": "https://github.com/hernancollazo/terminator-snipbox/issues",
        "Source": "https://github.com/hernancollazo/terminator-snipbox",
    },
)
