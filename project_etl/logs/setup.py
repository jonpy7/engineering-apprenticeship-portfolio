"""Setup script for the ETL pipeline package."""

from setuptools import setup, find_packages

setup(
    name="etl-pipeline",
    version="0.1.0",
    description="A production-ready ETL pipeline demonstrating data engineering best practices",
    author="Jon Batista",
    author_email="jontechalta@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.1.0",
        "sqlalchemy>=2.0.0",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "colorlog>=6.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)