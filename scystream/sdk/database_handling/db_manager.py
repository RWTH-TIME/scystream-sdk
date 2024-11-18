from pydantic import BaseModel


class PostgresConfig(BaseModel):
    """
    Configurations needed to setup the DatabaseOperations class
    """
    pg_user: str
    pg_pass: str
    pg_url: str


class DatabaseOperations:
    """
    This class handles all our database operations.
    For now, we are limited to Postgres databases.
    However, for extention see the FileOperations class
    """

    def __init__(self, spark_session, db_config):
        self.spark_session = spark_session
        self.db_config: PostgresConfig = db_config

    def insert_data(self, dataframe, table_name):
        dataframe.write \
            .format("jdbc") \
            .option("url", self.db_config.db_url) \
            .option("dbtable", table_name) \
            .option("user", self.db_config.pg_user) \
            .option("password", self.db_config.password) \
            .mode("append") \
            .save()

    def query_data(self, query):
        return self.spark_session.sql(query)
