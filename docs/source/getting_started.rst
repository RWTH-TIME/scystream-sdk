Getting started
================

Install the scystream-sdk:

.. code-block:: bash
   
    pip install scystream-sdk

Introduction
------------

One of the central concepts of scystream are the so-called **Compute Blocks**.

A Compute Block describes an independent program that acts as a worker,
which will be scheduled using the scystream-core application. This worker
executes a task (e.g. an NLP task, a crawling task).

This SDK provides helper function and all other requirements needed to implement
a custom Compute Block.

Each worker can have multiple entry points, each aimed at solving one task.
These entrypoints can be configured externally using **Settings**, which are
essentially environment variables parsed and validated using pydantic.

You can set "global" Setting (for the entrypoint) using the `envs` block,
or set "input/output-related" Settings using the config block in each input/output.

Basic Usage of the SDK
----------------------

.. code-block:: python 
   :emphasize-lines: 4,8

    from scystream.sdk.core import entrypoint
    from scystream.sdk.scheduler import Scheduler

    @entrypoint()
    def example_task():
        print("Executing example_task")

    @entrypoint()
    def another_task(task_name):
        print(f"Executing another_task with task name: {task_name}")

    def main():
        """
        The Scheduler functions are primarily used by the Scheduler in scystream-core to trigger
        the execution of entrypoints. However, you can also use it to trigger your functions manually.
        """
        Scheduler.list_entrypoints()
        Scheduler.execute_function("example_task")
        Scheduler.execute_function("another_task", "Scheduled Task")

    if __name__ == "__main__":
        main()

How to Define and Use Settings
------------------------------

Earlier, we were already talking about **Settings**.
Each Input & Output can be configured using these settings.

There are also Global Settings, refered to as `envs` in the `cbc.yaml`

Below you can find a simple example of how to extend the previously created entrypoints by settings.
Therefore you should use the  `EnvSettings` class.

.. code-block:: python
   :emphasize-lines: 6,13,20,27,28,31,32

    from scystream.sdk.core import entrypoint
    from scystream.sdk.env.settings import EnvSettings, InputSettings, OutputSettings
    
    # Assuming the Input of your Task is a database table.
    # You can define this in whatever form
    class ExampleTaskDBInput(InputSettings):
        PG_USER: str = "postgres"
        PG_PASS: str = "postgres"
        PG_HOST: str = "postgres"
        TABLE_NAME: str = "example_table"
    
    # Assuming the Ouput of you Task is a File.
    class ExampleTaskFileOutput(OutputSettings):
        S3_URL: str = "minio://minio:1234"
        S3_ACCESS: str = "access"
        S3_TOKEN: str = "token"
        FILE_NAME: str # this variable e.g. has to be set by in the envs, or the validation will fail
    
    # The "global" settings for the Entrypoint
    class ExampleTaskSettings(EnvSettings):
        LANGUAGE: str = "de"

        pg_input: ExampleTaskDBInput
        file_output: ExampleTaskFileOutput
    
    # pass it into the Entrypoint here
    @entrypoint(ExampleTaskSettings)
    def example_task(settings):
        print("You can use your variables now in your entrypoint.")
        
        print(f"Look at this: {settings.pg_input.PG_USER}")
        print(f"Or this: {settings.file_output.FILE_NAME}")

        print("Executing example_task")

Configure the SDK
------------------

You can configure three aspects of the SDK.

1. The `app_name` (which will be shown in the Apache Spark Control Plane)

2. The `cb_spark_master` (which defines the externally reachable URL of the Spark Master)

3. The `config_path` (configures the path for your `cbc.yaml`)

You can configure it like the following:

.. code-block:: python
    
    from scystream.sdk.config import SDKConfig

    SDKConfig(
        app_name="test_app"
        cb_spark_master="local[*]"
        config_path="configs/cb_config.yaml"
    )

    print("The rest of your code.")



Compute Block Config File
-------------------------

Every repository which will be used within the scystream application must
contain a **Compute Block Config File**, the `cbc.yaml`, within the root directory.

This `cbc.yaml` will be used to define the entrypoints, the inputs & outputs each
Compute Block offers, necessary for the scystream-core application to understand.

**ATTENTION**: When executing entrypoints, the cbc.yaml and the defined Settings will be
cross-validated! So make sure the `cbc.yaml` is always up-to-date with your code!

For the Code we previously wrote, this is an example `cbc.yaml`:

.. code-block:: yaml

    name: "Example Compute Block"
    description: "Contains examples"
    author: "John Doe"
    docker_image: "https://ghcr.io/nlp-toolbox"

    entrypoints:
      example_task:
        description: "Run example"
        envs:
          LANGUAGE: "de"
        inputs:
          pg_input:
          description: "Postgres input example"
          type: "db_table"
          config:
            PG_USER: "postgres"
            PG_PASS: "postgres"
            PG_HOST: "postgres"
            TABLE_NAME: "example_table"
        outputs:
          file_output:
            type: "file"
            config:
              S3_URL: "minio://minio:1234"
              S3_ACCESS: "access"
              S3_TOKEN: "token"
              FILE_NAME: null


Validating the Config 
^^^^^^^^^^^^^^^^^^^^^

You can validate you config like this:

.. code-block:: python
    
    from scystream.sdk.config import validate_config_with_code
    
    @entrypoint
    def example_entrypoint():
        print("Example")

    if __name__ == "__main__":
        validate_config_with_code()

Generating the Config
^^^^^^^^^^^^^^^^^^^^^^

If you didn't write the `cbc.yaml` on your own, and already have some entrypoints implemented,
you can also generate the `cbc.yaml` automatically.

.. code-block:: python
    
    from scystream.sdk.config import generate_config_from_compute_block, get_compute_block
    from pathlib import Path
    
    @entrypoint()
    def example_entrypoint():
        print("Example...")

    if __name__ == "__main__":
        compute_block = get_compute_block()
        generate_config_from_compute_block(compute_block, Path("cbc.yaml"))

Using a Database
----------------

The SDK has utilities implemented to query to & from a postgres database.
Therefore its using Apache Spark.

To interact with a database you have to do the following:

1. You have to create a Spark connection :class:`scystream.sdk.spark_manager.SparkManager`

2. Configure your Postgres connection using the :class:`scystream.sdk.database_handling.postgres_manager.PostgresConfig`

3. Setup Postgres in your Spark Session :meth:`scystream.sdk.spark_manager.SparkManager.setup_pg`

4. Interact with the Database using :mod:`scystream.sdk.database_handling.postgres_manager`!


See a simple example here:

.. code-block:: python
   :emphasize-lines: 6, 8, 15, 18, 24, 32
    
    from scystream.sdk.spark_manager import SparkManager
    from scystream.sdk.database_handling.postgres_manager import PostgresConfig

    @entrypoint()
    def test():
        manager = SparkManager()
        
        database_conf = PostgresConfig(
            pg_user="postgres",
            pg_pass="postgres",
            pg_host="postgres",
            pg_port=5432
        )
        
        db_conn = manager.setup_pg(database_conf)
        
        # Use sparks dataframes
        spark_df = manager.session.createDataFrame({
            Row(id=1, name="test"),
            Row(id=2, name="test")
        })

        # Write to the database
        db_conn.write(
            database_name="postgres",
            dataframe=spark_df,
            table="test",
            mode="overwrite"
        )

        # Read from the database
        read_df = db_conn.read(
            database_name="postgres",
            query=f"SELECT id FROM test WHERE id > 1"
        )
         
Using a S3 Bucket
-----------------

The SDK has utilities implemented to up- & download from a S3 Bucket.
Currently, it's *NOT* using Apache Spark for that.

To interact with a S3 Bucket you have to do the following:

1. Configure the S3 Connection using the :class:`scystream.sdk.file_handling.s3_manager.S3Config`

2. Setup the S3 Connection using the :class:`scystream.sdk.file_handling.s3_manager.S3Operations`

3. Use the Operations

See a simple example here:

.. code-block:: python
    :emphasize-lines: 5, 12, 14, 20

    from scystream.sdk.file_handling.s3_manager import S3Config, S3Operations

    @entrypoint()
    def test():
        s3_conf = S3Config(
            access_key="access",
            secret_key="secret",
            endpoint="http://localhost",
            post=9000
        )

        s3_conn = S3Operations(s3_conf)

        s3_conn.upload_file(
            path_to_file="path/test.txt",
            bucket_name="Example",
            target_name="target_file_name.txt"
        )

        s3_conn.download_file(
            bucket_name="Example",
            s3_object_name="target_file_name.txt",
            local_file_path="download.txt"
        )
