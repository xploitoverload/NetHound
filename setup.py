from setuptools import setup, find_packages

setup(
    name="nethound",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pypdf>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nethound = nethound.cli:main",
        ],
    },
)
