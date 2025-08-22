from setuptools import setup, find_packages

setup(
    name="small_redbook",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "langchain>=0.3.0",
        "langchain-openai>=0.2.0",
        "feedparser>=6.0.11",
        "requests>=2.32.3",
        "beautifulsoup4>=4.12.3",
        "schedule>=1.2.2",
        "playwright>=1.54.0",
        "httpx>=0.27.0",
        "python-dotenv>=1.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.9",
)