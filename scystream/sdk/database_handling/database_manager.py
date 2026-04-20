from abc import ABC, abstractmethod
from urllib.parse import urlparse
from pyspark.sql import SparkSession, DataFrame

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.sql import quoted_name


class BaseDatabaseOperations(ABC):
    MAX_TABLE_NAME_LENGTH = 63

    def __init__(self, dsn: str, schema: str | None = None):
        self.dsn = dsn
        self.schema = self._normalize_schema(schema)

    def _validate_table_name(self, table: str):
        if len(table) > self.MAX_TABLE_NAME_LENGTH:
            raise ValueError(
                f"Table name '{table}' exceeds {self.MAX_TABLE_NAME_LENGTH}\
                        characters."
            )

    def _validate_read_inputs(
        self,
        table: str | None,
        query: str | None,
    ):
        if not table and not query:
            raise ValueError("Either 'table' or 'query' must be provided.")

        if table:
            self._validate_table_name(table)

    @staticmethod
    def _normalize_schema(schema: str | None) -> str | None:
        if schema is None:
            return None
        schema = schema.strip()
        return schema or None

    @abstractmethod
    def read(
        self,
        table: str | None = None,
        query: str | None = None,
    ):
        pass

    @abstractmethod
    def write(
        self,
        table: str,
        data,
        mode: str = "overwrite",
    ):
        pass


class SparkDatabaseOperations(BaseDatabaseOperations):
    """
    Class to perform PostgreSQL operations using Apache Spark.

    This class provides methods to read from and write to a PostgreSQL database
    using JDBC and Spark's DataFrame API. It requires a SparkSession and a
    PostgresConfig object or the PostgresSettings from an input or output for
    database connectivity.
    """

    def __init__(self, spark: SparkSession, dsn: str, schema: str | None):
        super().__init__(dsn, schema)
        self.spark_session = spark

        self.jdbc_url, self.properties = self._dsn_to_jdbc(dsn)

        self.properties = {
            "driver": "org.postgresql.Driver",
        }

    def _dsn_to_jdbc(self, dsn: str) -> tuple[str, dict]:
        """
        Convert SQLAlchemy DSN to JDBC URL and connection properties.
        """

        parsed = urlparse(dsn)
        if not parsed.hostname:
            raise ValueError("Invalid DSN: missing hostname")

        # Build JDBC URL
        jdbc_url = (
            f"jdbc:postgresql://{parsed.hostname}:"
            f"{parsed.port or 5432}{parsed.path}"
        )

        # Extract credentials
        properties = {
            "driver": "org.postgresql.Driver",
        }

        if parsed.username:
            properties["user"] = parsed.username

        if parsed.password:
            properties["password"] = parsed.password

        return jdbc_url, properties

    def read(
        self,
        table: str | None = None,
        query: str | None = None,
    ) -> DataFrame:
        """
        Reads data from a PostgreSQL database into a Spark DataFrame.

        This method can either read data from a specified table or execute a
        custom SQL query
        to retrieve data from the database.

        :param table: The name of the table to read data from. Must be provided
            if `query` is not supplied. (optional)
        :param query: A custom SQL query to run. If provided, this overrides
            the `table` parameter. (optional)

        :return: A Spark DataFrame containing the result of the query or
            table data.
        :rtype: DataFrame
        """
        self._validate_read_inputs(table, query)

        if query:
            dbtable_option = f"({query}) AS subquery"
        else:
            dbtable_option = f"{self.schema}.{table}" if self.schema else table

        return (
            self.spark_session.read.format("jdbc")
            .option("url", self.jdbc_url)
            .option("dbtable", dbtable_option)
            .options(**self.properties)
            .load()
        )

    def write(
        self,
        table: str,
        dataframe,
        mode="overwrite",
        schema: str | None = None,
    ):
        """
        Writes a Spark DataFrame to a specified table in a PostgreSQL database
        using JDBC.

        This method writes the provided DataFrame to the target PostgreSQL
        table, with the option to specify the write mode (overwrite, append,
                                                          etc.).

        :param table: The name of the table where data will be written.
        :param dataframe: The Spark DataFrame containing the data to write.
        :param mode: The write mode. Valid options are 'overwrite', 'append',
            'ignore', and 'error'. Defaults to 'overwrite'. (optional)

        :note: Ensure that the schema of the DataFrame matches the schema of
            the target table if the table exists.
        :note: The `mode` parameter controls the behavior when the table
            already exists.
        """
        self._validate_table_name(table)

        dbtable_option = f"{schema}.{table}" if self.schema else table

        (
            dataframe.write.format("jdbc")
            .option("url", self.jdbc_url)
            .option("dbtable", dbtable_option)
            .options(**self.properties)
            .mode(mode)
            .save()
        )


class PandasDatabaseOperations(BaseDatabaseOperations):
    """
    Database operations using Pandas and SQLAlchemy.

    This class provides a simple interface to read from and write to any
    SQLAlchemy-compatible database using Pandas DataFrames. The connection
    is established via a DSN (Data Source Name), making this implementation
    backend-agnostic.

    Supported databases include (but are not limited to):
    - PostgreSQL
    - MySQL
    - SQLite
    - Snowflake
    - Oracle

    This implementation is best suited for local or small-to-medium sized
    datasets where distributed processing (e.g., Spark) is not required.
    """

    def __init__(self, dsn: str, schema: str | None = None):
        """
        Initialize the PandasDatabaseOperations instance.

        :param dsn: A SQLAlchemy-compatible database connection string
            (DSN), e.g.:
            - postgresql://user:pass@host:5432/db
            - mysql+pymysql://user:pass@host/db
            - sqlite:///local.db
        :param schema: An optional schema used in postgres databases can be
            specified

        :raises ValueError: If the DSN is invalid or connection fails.

        :note: Uses SQLAlchemy's connection pooling with `pool_pre_ping=True`
            to ensure stale connections are automatically refreshed.
        """
        super().__init__(dsn, schema)
        self.engine = create_engine(dsn, pool_pre_ping=True)

    def read(
        self,
        table: str | None = None,
        query: str | None = None,
    ) -> pd.DataFrame:
        """
        Read data from the database into a Pandas DataFrame.

        This method supports two modes of operation:
        - Reading all rows from a specified table
        - Executing a custom SQL query

        :param table: The name of the table to read from. Must be provided
            if `query` is not supplied. (optional)
        :param query: A custom SQL query to execute. If provided, this
            overrides the `table` parameter. (optional)

        :raises ValueError: If neither `table` nor `query` is provided.
        :raises ValueError: If the table name exceeds the allowed length.

        :return: A Pandas DataFrame containing the query result.
        :rtype: pandas.DataFrame

        :example:
            >>> db.read(table="users")
            >>> db.read(query="SELECT id, name FROM users WHERE active = true")
        """
        self._validate_read_inputs(table, query)

        if table:
            if self.schema:
                query = f'SELECT * FROM "{self.schema}"."{table}"'
            else:
                query = f'SELECT * FROM "{table}"'

        return pd.read_sql(text(query), self.engine)

    def write(
        self,
        table: str,
        data: pd.DataFrame,
        mode: str = "overwrite",
    ):
        """
        Write a Pandas DataFrame to the database.

        This method writes the provided DataFrame to the specified table
        using SQLAlchemy. The behavior when the table already exists is
        controlled via the `mode` parameter.

        :param table: The name of the target table.
        :param data: The Pandas DataFrame to write.
        :param mode: The write mode. Supported options are:
            - 'overwrite': Replace the table if it exists.
            - 'append': Append data to the existing table.
            Defaults to 'overwrite'. (optional)

        :raises ValueError: If the table name exceeds the allowed length.
        :raises ValueError: If an unsupported mode is provided.

        :note:
            - The DataFrame index is not written to the database.
            - Ensure schema compatibility when using `mode='append'`.

        :example:
            >>> db.write("users", df)
            >>> db.write("users", df, mode="append")
        """
        self._validate_table_name(table)

        if mode == "overwrite":
            if_exists = "replace"
        elif mode == "append":
            if_exists = "append"
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        table_name = quoted_name(table, quote=True)

        data.to_sql(
            name=table_name,
            con=self.engine,
            schema=self.schema,
            if_exists=if_exists,
            index=False,
        )
