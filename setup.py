from setuptools import setup, find_packages

setup(
    name="scystream-sdk",
    version="1.4.0",
    description="The official SDK for developing scystream compute blocks",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/RWTH-TIME/scystream-sdk",
    author="Felix Evers, Paul Kalhorn",
    author_email="evers@time.rwth-aachen.de, kalhorn@time.rwth-aachen.de",
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
        "boto3>=1.35.65",
        "setuptools>=65.0.0",
    ],
    extras_require={
        "database": [
            "pandas>=2.0.0",
            "SQLAlchemy>=2.0.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.9",
        ],
        "mysql": [
            "PyMySQL>=1.1.0",
        ],
        "snowflake": [
            "snowflake-sqlalchemy>=1.7.7",
        ],
        "oracle": [
            "oracledb>=3.4.0",
        ],
        "odbc": [
            "pyodbc>=5.2.0",
        ],
        "duckdb": [
            "duckdb>=1.4.0",
        ],
        "all": [
            "pandas>=2.0.0",
            "SQLAlchemy>=2.0.0",
            "psycopg2-binary>=2.9.9",
            "PyMySQL>=1.1.0",
            "snowflake-sqlalchemy>=1.7.7",
            "oracledb>=3.4.0",
            "pyodbc>=5.2.0",
            "duckdb>=1.4.0",
        ],
        "dev": [
            "sphinx>=8.1.3",
            "sphinx-autodoc-typehints>=2.5.0",
            "sphinxawesome-theme>=5.3.2",
            "Pygments>=2.18.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
