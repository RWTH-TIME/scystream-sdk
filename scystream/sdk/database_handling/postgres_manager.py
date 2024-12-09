from pyspark.sql import SparkSession, DataFrame
from pydantic import BaseModel


class PostgresConfig(BaseModel):
    """
    Configurations needed to setup the DatabaseOperations class
    """
    pg_user: str
    pg_pass: str
    pg_host: str
    pg_port: int


class PostgresOperations():
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
        Reads data from a database using a table name or custom query.

        :param database_name: Name of the database.
        :param table: Name of the table to read from. Required if `query` is
        not provided.
        :param query: Custom SQL query. Overrides `table` if provided.
        :return: A Spark DataFrame containing the queried data.
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
        Writes a DataFrame to a specified table in a PostgreSQL database using
        JDBC.

        Parameters:
        - database_name (str): Name of the database to connect to.
        - table (str): Name of the table where data will be written.
        - dataframe (DataFrame): The Spark DataFrame containing the data
        to write.
        - mode (str, optional): The write mode ('overwrite', 'append',
                                                'ignore', or 'error').
                                Defaults to 'overwrite'.

        Notes:
        - Ensure that if the target table exists the schema of the dataframe
        matches the schema of the table.
        """

        db_url = f"{self.jdbc_url}/{database_name}"
        dataframe.write.format("jdbc")\
            .option("url", db_url) \
            .option("dbtable", table) \
            .options(**self.properties) \
            .mode(mode) \
            .save()
