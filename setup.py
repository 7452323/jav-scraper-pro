from setuptools import setup, find_packages

setup(
    name="jav-scraper-pro",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pillow>=10.0.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jav-scraper=jav_scraper.cli:main",
        ],
    },
    python_requires=">=3.9",
)
