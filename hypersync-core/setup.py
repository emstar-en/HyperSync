from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hypersync-core",
    version="1.0.0",
    author="HyperSync Team",
    author_email="team@hypersync.ai",
    description="Open-source geometric operations library with 43 Core tier operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emstar-en/HyperSync",
    project_urls={
        "Bug Tracker": "https://github.com/emstar-en/HyperSync/issues",
        "Documentation": "https://github.com/emstar-en/HyperSync/tree/main/hypersync-core/docs",
        "Source Code": "https://github.com/emstar-en/HyperSync",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: System :: Distributed Computing",
    ],
    package_dir={"":  "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    keywords="geometry hyperbolic spherical consensus byzantine-fault-tolerance distributed-systems",
)
