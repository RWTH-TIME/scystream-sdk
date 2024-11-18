from pyspark.sql import SparkSession
from scystream.sdk.config import SDKConfig
from scystream.sdk.database_handling.db_manager import DatabaseOperations, \
    PostgresConfig
from scystream.sdk.file_handling.s3_manager import S3Config, FileOperations


class SparkManager:
    def __init__(self, config):
        self.config: SDKConfig = config
        self.spark = SparkSession.builder \
            .master(self.config.master) \
            .appName(self.config.app_name) \
            .getOrCreate()
        self.file_ops = None
        self.db_ops = None

    def setup_db(self, config: PostgresConfig):
        self.file_ops = DatabaseOperations(config)

    def setup_s3(self, config: S3Config):
        self.db_ops = FileOperations(config)

    def upload_file(self, file_path):
        if self.file_ops:
            self.file_ops.upload_file()
        # TODO: logging

    def download_file(self, file_path):
        if self.file_ops:
            # TODO
            print("TODO")

    def stop_session(self):
        if self.spark:
            self.spark.stop()
            self.spark = None
            self.file_ops = None
            self.db_ops = None
