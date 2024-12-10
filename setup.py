from setuptools import setup, find_packages

setup(
    name="loggerx",
    version="0.1.0",
    author="Python Dev Team",
    author_email="samir21101993@hotmail.com",
    description="A wrapper for Python logging with exception handling and stack traces that also supports Graylog.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Samir55380/loggerX",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["graypy"],
)
