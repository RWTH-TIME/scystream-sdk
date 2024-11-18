from pydantic import BaseModel
from pyspark.sql import SparkSession


class S3Config(BaseModel):
    connection_name: str
    access_key: str
    secret_key: str
    endpoint: str


class S3Operations():
    # TODO: What are we doing when the access_token etc. needs to be refreshed
    # In shoutout we used presigned urls, do we need them here aswell?

    def __init__(self, spark: SparkSession, config: S3Config):
        self.spark_session = spark
        self.config = config

    def load_df(self, bucket_name: str, path: str):
        return self.spark_session.read \
            .format("parquet") \
            .option("spark.hadoop.fs.s3a.access.key", self.config.access_key) \
            .option("spark.hadoop.fs.s3a.secret.key", self.config.secret_key) \
            .option("spark.hadoop.fs.s3a.endpoint", self.config.endpoint) \
            .load(path)

    # TODO: Think about other types and up/download to/from local file path
