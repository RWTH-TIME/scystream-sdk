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
    include_package_data=True,
    package_data={
        "scystream.sdk": [
            "spark_jars/postgresql-42.7.4.jar",
        ]
    },
    install_requires=[
        "pydantic>=2.9.2",
        "PyYAML>=6.0.2",
        "pydantic-settings>=2.6.1",
        "pyspark>=3.5.3",
        "setuptools>=75.5.0",
        "boto3>=1.35.65"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
