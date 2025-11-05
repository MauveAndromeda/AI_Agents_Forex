"""
Setup script for Forex DeepSeeker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="forex-deepseeker",
    version="1.0.0",
    author="MauveAndromeda",
    description="AI-Enhanced Multi-Timeframe Forex Trading System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MauveAndromeda/AI_Agents_Forex",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "forex-backtest=quick_backtest:main",
            "forex-live=run_live_strategy:main",
            "forex-visualize=tools.visualize_results:main",
        ],
    },
)
