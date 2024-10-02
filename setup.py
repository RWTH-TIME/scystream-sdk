from setuptools import setup, find_packages

setup(
    name="scystream-sdk",
    version="0.1.4",
    description="The official SDK for developing scystream compute blocks",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/RWTH-TIME/scystream-sdk",
    author="Felix Evers",
    author_email="evers@time.rwth-aachen.de",
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
