from pyspark.sql import SparkSession
from scystream.sdk.config import SDKConfig
from scystream.sdk.file_handling.s3_manager import S3Config, S3Operations
from scystream.sdk.database_handling.postgres_manager import \
    PostgresConfig, PostgresOperations


class SparkManager:
    def __init__(self):
        self.config: SDKConfig = SDKConfig()
        self.session = SparkSession.builder \
            .master(self.config.cb_spark_master) \
            .appName(self.config.app_name) \
            .getOrCreate()

    def setup_pg(self, config: PostgresConfig):
        """
        TODO: centralize config, the datasources (PostgresConfig, S3Config) 
        inherit from, so that connection_name is always set
        """
        return PostgresOperations(self.session, config)

    def setup_s3(self, config: S3Config):
        return S3Operations(self.session, config)

    def stop_session(self):
        if self.spark:
            self.spark.stop()
            self.spark = None
            self.file_ops = None
            self.db_ops = None
