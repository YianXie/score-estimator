"""Setup script for the OGS Score Estimator Python package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ogs-score-estimator",
    version="1.0.0",
    author="OGS Contributors",
    description="Go score estimator and dead stone removal suggester (Python port)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YianXie/score-estimator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    keywords="go baduk weiqi score estimator dead stones",
)
