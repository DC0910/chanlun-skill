"""
缠论股票分析 OpenClaw Skill 安装配置
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chanlun-stock-analysis",
    version="1.0.0",
    author="ChanLun Team",
    author_email="chanlun@example.com",
    description="基于缠论理论的股票分析 OpenClaw Skill",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chanlun/chanlun-stock-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "openclaw.skills": [
            "chanlun-stock-analysis = chanlun_stock_analysis.skill:create_skill"
        ]
    },
    include_package_data=True,
    package_data={
        "chanlun_stock_analysis": ["*.yaml", "*.json"],
    },
    zip_safe=False,
)
