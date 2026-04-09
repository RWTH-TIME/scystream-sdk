import pkg_resources
from pyspark.sql import SparkSession

from scystream.sdk.config import SDKConfig
from scystream.sdk.database_handling.database_manager import (
    SparkDatabaseOperations,
)


class SparkManager:
    def __init__(self):
        self.config: SDKConfig = SDKConfig()

        psql_jar_path = pkg_resources.resource_filename(
            "scystream.sdk",
            "spark_jars/postgresql-42.7.4.jar",
        )

        """
        When starting the ComputeBlock using Apache Spark's DockerOperator,
        ensure that the container runs in the same network as the spark-master
        and spark-worker nodes. Otherwise, Spark jobs may fail.
        """

        self.session = (
            SparkSession.builder.master(self.config.cb_spark_master)
            .appName(self.config.app_name)
            .config("spark.jars", psql_jar_path)
            .getOrCreate()
        )

    def setup_pg(self, dsn: str) -> SparkDatabaseOperations:
        if not dsn.startswith("postgresql://"):
            raise ValueError(
                "Spark integration currently only supports PostgreSQL DSNs."
            )

        return SparkDatabaseOperations(self.session, dsn)

    def stop_session(self):
        if self.session:
            self.session.stop()
            self.session = None
