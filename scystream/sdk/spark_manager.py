import pkg_resources
from pyspark.sql import SparkSession
from scystream.sdk.config import SDKConfig
from scystream.sdk.database_handling.postgres_manager import \
    PostgresConfig, PostgresOperations


class SparkManager:
    def __init__(self):
        self.config: SDKConfig = SDKConfig()

        psql_jar_path = pkg_resources.resource_filename(
            "scystream.sdk", "spark_jars/postgresql-42.7.4.jar"
        )

        """
        When starting the ComputeBlock using Apache Sparks DockerOperator
        we need to make sure, to start the container in the same network
        as the spark-worker and the spark-master.
        Else, the spark jobs will not be executed correctly.
        """
        self.session = SparkSession.builder \
            .master(self.config.cb_spark_master) \
            .appName(self.config.app_name) \
            .config("spark.jars", psql_jar_path) \
            .getOrCreate()

    def setup_pg(self, config: PostgresConfig):
        return PostgresOperations(self.session, config)

    def stop_session(self):
        if self.spark:
            self.spark.stop()
            self.spark = None
