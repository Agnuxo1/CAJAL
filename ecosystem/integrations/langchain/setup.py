from setuptools import setup, find_packages

setup(
    name="cajal-langchain",
    version="1.0.0",
    description="LangChain integration for CAJAL-4B scientific intelligence model",
    author="P2PCLAW Lab",
    author_email="contact@p2pclaw.com",
    packages=find_packages(),
    install_requires=[
        "langchain-core>=0.1.0",
        "requests>=2.32.0",
    ],
    python_requires=">=3.9",
    url="https://github.com/p2pclaw/cajal-langchain",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
