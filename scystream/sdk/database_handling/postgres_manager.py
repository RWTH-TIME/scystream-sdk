from abc import ABC, abstractmethod
from pyspark.sql import SparkSession, DataFrame
from pydantic import BaseModel
from scystream.sdk.env.settings import PostgresSettings

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.sql import quoted_name


class PostgresConfig(BaseModel):
    """
    Configuration class for PostgreSQL connection details.

    This class holds the necessary configuration parameters to connect to a
    PostgreSQL database. It includes the database user, password, host, and
    port.

    :param PG_USER: The username for the PostgreSQL database.
    :param PG_PASS: The password for the PostgreSQL database.
    :param PG_HOST: The host address of the PostgreSQL server.
    :param PG_PORT: The port number of the PostgreSQL server.
    """

    PG_USER: str
    PG_PASS: str
    PG_HOST: str
    DB_NAME: str
    PG_PORT: int


class BasePostgresOperations(ABC):
    MAX_TABLE_NAME_LENGTH = 63

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

    @abstractmethod
    def read(
        self,
        table: str | None = None,
        query: str | None = None,
    ):
        pass

    @abstractmethod
    def write(self, table: str, data, mode: str = "overwrite"):
        pass


class SparkPostgresOperations(BasePostgresOperations):
    """
    Class to perform PostgreSQL operations using Apache Spark.

    This class provides methods to read from and write to a PostgreSQL database
    using JDBC and Spark's DataFrame API. It requires a SparkSession and a
    PostgresConfig object or the PostgresSettings from an input or output for
    database connectivity.
    """

    def __init__(
        self, spark: SparkSession, config: PostgresConfig | PostgresSettings
    ):
        self.spark_session = spark
        self.jdbc_url = f"jdbc:postgresql://{config.PG_HOST}:{config.PG_PORT}/{config.DB_NAME}"
        self.properties = {
            "user": config.PG_USER,
            "password": config.PG_PASS,
            "driver": "org.postgresql.Driver",
        }

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

        :param database_name: The name of the database to connect to.
        :param table: The name of the table to read data from. Must be provided
            if `query` is not supplied. (optional)
        :param query: A custom SQL query to run. If provided, this overrides
            the `table` parameter. (optional)

        :raises ValueError: If neither `table` nor `query` is provided.

        :return: A Spark DataFrame containing the result of the query or
            table data.
        :rtype: DataFrame
        """
        self._validate_read_inputs(table, query)

        db_url = f"{self.jdbc_url}"
        dbtable_option = f"({query}) AS subquery" if query else table

        return (
            self.spark_session.read.format("jdbc")
            .option("url", db_url)
            .option("dbtable", dbtable_option)
            .options(**self.properties)
            .load()
        )

    def write(self, table: str, dataframe, mode="overwrite"):
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

        db_url = f"{self.jdbc_url}"
        dataframe.write.format("jdbc").option("url", db_url).option(
            "dbtable", table
        ).options(**self.properties).mode(mode).save()


class PandasPostgresOperations(BasePostgresOperations):
    """
    Class to perform PostgreSQL operations using Pandas and SQLAlchemy.

    This class provides methods to read from and write to a PostgreSQL database
    using SQLAlchemy and Pandas DataFrames. It requires a PostgresConfig or
    PostgresSettings object for database connectivity.

    Compared to the Spark-based implementation, this class is intended for
    local, non-distributed workloads and is recommended when working with
    smaller datasets.
    """

    def __init__(self, config: PostgresConfig | PostgresSettings):
        """
        Initialize the PandasPostgresOperations instance.

        :param config: Configuration object containing PostgreSQL connection
            details. Can be either PostgresConfig or PostgresSettings.
        """
        self.config = config
        self.engine = create_engine(
            f"postgresql+psycopg2://{config.PG_USER}:{config.PG_PASS}"
            f"@{config.PG_HOST}:{int(config.PG_PORT)}/{config.DB_NAME}"
        )

    def read(
        self,
        table: str | None = None,
        query: str | None = None,
    ) -> pd.DataFrame:
        """
        Reads data from a PostgreSQL database into a Pandas DataFrame.

        This method can either read all data from a specified table or execute
        a custom SQL query.

        :param table: The name of the table to read data from. Must be provided
            if `query` is not supplied. (optional)
        :param query: A custom SQL query to execute. If provided, this\
            overrides the `table` parameter. (optional)

        :raises ValueError: If neither `table` nor `query` is provided.
        :raises ValueError: If the table name exceeds PostgreSQL's maximum
            length (63 characters).

        :return: A Pandas DataFrame containing the result of the query or
            table data.
        :rtype: pandas.DataFrame
        """
        self._validate_read_inputs(table, query)

        if table:
            query = f'SELECT * FROM "{table}"'

        return pd.read_sql(text(query), self.engine)

    def write(
        self,
        table: str,
        data: pd.DataFrame,
        mode: str = "overwrite",
    ):
        """
        Writes a Pandas DataFrame to a specified table in a PostgreSQL\
        database.

        This method writes the provided DataFrame to the target PostgreSQL
        table using SQLAlchemy. The behavior when the table already exists is
        controlled via the `mode` parameter.

        :param table: The name of the table where data will be written.
        :param data: The Pandas DataFrame containing the data to write.
        :param mode: The write mode. Supported options are:
            - 'overwrite': Replaces the table if it exists.
            - 'append': Appends data to the existing table.
            Defaults to 'overwrite'. (optional)

        :raises ValueError: If the table name exceeds PostgreSQL's maximum
            length (63 characters).
        :raises ValueError: If an unsupported write mode is provided.

        :note: Ensure that the schema of the DataFrame matches the schema of
            the target table if the table already exists and `mode='append'`.
        :note: Index columns of the DataFrame are not written to the database.
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
            table_name,
            self.engine,
            if_exists=if_exists,
            index=False,
        )
