from pyspark.sql import SparkSession, DataFrame
from pydantic import BaseModel


class PostgresConfig(BaseModel):
    """
    Configurations needed to setup the DatabaseOperations class
    """
    connection_name: str
    pg_user: str
    pg_pass: str
    pg_host: str
    pg_port: int


class PostgresOperations():
    def __init__(self, spark: SparkSession, config: PostgresConfig):
        self.spark_session = spark
        self.config = config
        self.jdbc_url = \
            f"jdbc:postgresql://{self.config.pg_host}:{self.config.pg_port}?user={self.config.pg_user}&password={self.config.pg_pass}"

    def read(self, table: str, query: str = None) -> DataFrame:
        if query:
            return self.spark.read.jdbc(
                self.jdbc_url,
                f"({query}) AS temp"
            )
        else:
            return self.spark.read.jdbc(self.jdbc_url, table)

    def write(
        self,
        dataframe: DataFrame,
        table: str,
        mode: str = "overwrite"
    ) -> None:
        dataframe.write.jdbc(self.jdbc_url, table, mode=mode)

    def query(self, query: str) -> DataFrame:
        return self.spark.read.jdbc(self.jdbc_url, f"({query}) AS temp")
