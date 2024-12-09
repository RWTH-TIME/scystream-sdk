from pyspark.sql import SparkSession, DataFrame
from pydantic import BaseModel


class PostgresConfig(BaseModel):
    """
    Configuration class for PostgreSQL connection details.

    This class holds the necessary configuration parameters to connect to a
    PostgreSQL database. It includes the database user, password, host, and
    port.

    :param pg_user: The username for the PostgreSQL database.
    :param pg_pass: The password for the PostgreSQL database.
    :param pg_host: The host address of the PostgreSQL server.
    :param pg_port: The port number of the PostgreSQL server.
    """
    pg_user: str
    pg_pass: str
    pg_host: str
    pg_port: int


class PostgresOperations():
    """
    Class to perform PostgreSQL operations using Apache Spark.

    This class provides methods to read from and write to a PostgreSQL database
    using JDBC and Spark's DataFrame API. It requires a SparkSession and a
    PostgresConfig object for database connectivity.
    """

    def __init__(self, spark: SparkSession, config: PostgresConfig):
        self.spark_session = spark
        self.jdbc_url = \
            f"jdbc:postgresql://{config.pg_host}:{config.pg_port}"
        self.properties = {
            "user": config.pg_user,
            "password": config.pg_pass,
            "driver": "org.postgresql.Driver"
        }

    def read(
            self,
            database_name: str,
            table: str = None,
            query: str = None
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
        if not table and not query:
            raise ValueError("Either 'table' or 'query' must be provided.")

        db_url = f"{self.jdbc_url}/{database_name}"

        dbtable_option = f"({query}) AS subquery" if query else table

        return self.spark_session.read \
            .format("jdbc") \
            .option("url", db_url) \
            .option("dbtable", dbtable_option) \
            .options(**self.properties) \
            .load()

    def write(
            self,
            database_name: str,
            table: str,
            dataframe,
            mode="overwrite"
    ):
        """
        Writes a Spark DataFrame to a specified table in a PostgreSQL database
        using JDBC.

        This method writes the provided DataFrame to the target PostgreSQL
        table, with the option to specify the write mode (overwrite, append,
                                                          etc.).

        :param database_name: The name of the database to connect to.
        :param table: The name of the table where data will be written.
        :param dataframe: The Spark DataFrame containing the data to write.
        :param mode: The write mode. Valid options are 'overwrite', 'append',
            'ignore', and 'error'. Defaults to 'overwrite'. (optional)

        :note: Ensure that the schema of the DataFrame matches the schema of
            the target table if the table exists.
        :note: The `mode` parameter controls the behavior when the table
            already exists.
        """

        db_url = f"{self.jdbc_url}/{database_name}"
        dataframe.write.format("jdbc")\
            .option("url", db_url) \
            .option("dbtable", table) \
            .options(**self.properties) \
            .mode(mode) \
            .save()
