"""
缠论股票分析 Skill 安装脚本
"""
from setuptools import setup, find_packages

setup(
    name='chanlun-stock-analysis',
    version='1.0.0',
    description='基于缠论理论的股票分析OpenClaw Skill',
    author='ChanLun Team',
    author_email='chanlun@example.com',
    packages=find_packages(),
    install_requires=[
        'openclaw-sdk>=1.0.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'matplotlib>=3.4.0',
        'tushare>=1.2.0',
        'akshare>=1.10.0',
        'pydantic>=1.8.0',
        'loguru>=0.6.0',
    ],
    entry_points={
        'openclaw.skills': [
            'chanlun = skill.main:ChanLunStockAnalysisSkill'
        ]
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
