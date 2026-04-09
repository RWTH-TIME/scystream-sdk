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

There are three types of input/output Settings that can be used: , `FileSettings`, `DatabaseSettings` or
`CustomSettings`.
File and Database Settings do have predefined settings, such as `DB_DSN`, `DB_TABLE` or `S3_HOST`.


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



Types of Inputs and Outputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^

We provide predefined setting types that include standardized environment variable keys for common use cases. These settings are designed to simplify configuration and ensure consistency across your project.

File Settings (``FileSettings``)
""""""""""""""""""""""""""""""""

Use the ``FileSettings`` class for configurations related to file-based inputs and outputs, such as S3 file storage. It includes the following standardized environment variable keys:

- ``S3_HOST``: The host address for the S3 service.
- ``S3_PORT``: The port for the S3 service.
- ``S3_ACCESS_KEY``: The access key for authenticating with the S3 service.
- ``S3_SECRET_KEY``: The secret key for authenticating with the S3 service.
- ``BUCKET_NAME``: The name of the S3 bucket.
- ``FILE_PATH``: The path to the file within the bucket.
- ``FILE_NAME``: The name of the file.
- ``FILE_EXT``: The extention of the file (without ".").

Database Settings (``DatabaseSettings``)
""""""""""""""""""""""""""""""""""""""""""

Use the ``DatabaseSettings`` class for configurations related to database inputs and outputs. It includes the following standardized environment variable keys:

- ``DB_DSN``: Full database connection string (SQLAlchemy compatible)
- ``DB_TABLE``: The name of the database table.

Usage Instructions
^^^^^^^^^^^^^^^^^^

To use these predefined settings, simply include them in your configuration as shown in the examples below.

Important Notes
---------------

1. **__identifier__ Requirement**:
   - When using ``FileSettings`` or ``DatabaseSettings``, you **must** define an ``__identifier__`` attribute in your input/output class.
   - The ``__identifier__`` is used to prefix the environment variable keys, ensuring that they do not conflict when multiple inputs or outputs of the same type are defined.
   - Make sure, that the ``__identifier__`` is unique across your project!

   Example:

   .. code-block:: python

      class MyFileInput(FileSettings, InputSettings):
          __identifier__ = "my_file_input"  # Prefixes env vars with `my_file_input_`

2. **Optional but Recommended**:
   - While you are not required to use these predefined settings, we strongly recommend them for file or PostgreSQL-based inputs and outputs to maintain consistency and avoid configuration errors.

Example Configuration
^^^^^^^^^^^^^^^^^^^^^

Here’s an example of how to define and use these settings in your project:

Below you can find a simple example of how to extend the previously created entrypoints by settings.
Therefore you should use the  `EnvSettings` class.

.. code-block:: python
   :emphasize-lines: 5,10,14,20,23,24,25,28,29

    from scystream.sdk.core import entrypoint
    from scystream.sdk.env.settings import EnvSettings, InputSettings, OutputSettings, FileSettings, DatabaseSettings

    # Assuming the Input of your Task is a database table.
    class ExampleTaskDBInput(DatabaseSettings, InputSettings):
        __identifier__ = "my_first_pg"
        pass

    # Assuming the Ouput of you Task is a File.
    class ExampleTaskFileOutput(FileSettings, OutputSettings):
        __identifier__ = "my_first_file"
        pass

    class CustomOutputConfigurable(OutputSettings):
        FB_USER: str = "RWTH"
        FB_PASS: str # this variable e.g. has to be set by in the envs, or the validation will fail


    # The "global" settings for the Entrypoint
    class ExampleTaskSettings(EnvSettings):
        LANGUAGE: str = "de"

        pg_input: ExampleTaskDBInput
        file_output: ExampleTaskFileOutput
        custom_output: CustomOutputConfigurable

    # pass it into the Entrypoint here
    @entrypoint(ExampleTaskSettings)
    def example_task(settings):
        print("You can use your variables now in your entrypoint.")

        print(f"Look at this: {settings.pg_input.DB_DSN}")
        print(f"Or this: {settings.file_output.FILE_NAME}")

        print("Executing example_task")


Configure the SDK
------------------

You can configure three aspects of the SDK.

1. The `app_name` (which will be shown in the Apache Spark Control Plane)

2. The `cb_spark_master` (which defines the externally reachable URL of the Spark Master)

You can configure it like the following:

.. code-block:: python

    from scystream.sdk.config import SDKConfig

    SDKConfig(
        app_name="test_app"
        cb_spark_master="local[*]"
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
            type: "database_table"
            config:
              my_first_pg_DB_DSN: null
              my_first_pg_DB_TABLE: null
        outputs:
          file_output:
            type: "file"
            config:
              my_first_file_BUCKET_NAME: null
              my_first_file_FILE_NAME: null
              my_first_file_FILE_PATH: null
              my_first_file_S3_ACCESS_KEY: null
              my_first_file_S3_HOST: null
              my_first_file_S3_PORT: null
              my_first_file_S3_SECRET_KEY: null
          custom_output:
            description: "custom description"
            type: "custom"
            config:
              FB_USER: "RWTH"
              FB_PASS: null


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

The SDK provides utilities to interact with a PostgreSQL database.
You can work with either:

- **Pandas DataFrames** (recommended for most use cases)
- **Apache Spark DataFrames** (for distributed workloads)

All database connections are configured via:

- :class:`scystream.sdk.env.settings.DatabaseSettings`


Configuration
^^^^^^^^^^^^^

You can configure your Databse in the following way.

**Use DatabaseSettings (recommended in pipelines)**

.. code-block:: python

    from scystream.sdk.env.settings import DatabaseSettings

    class MyDatabaseSettings(DatabaseSettings):
        __identifier__ = "MY_DB"

The following environment variables must be provided:

As the DB_DSN variable, you can use all SQLAlchemy supported DSNs

.. code-block:: bash

    MY_DB_DB_DSN=postgresql://user:pass@host:5432/db
    MY_DB_DB_TABLE=my_table


Working with Pandas DataFrames
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Pandas integration is the simplest way to interact with PostgreSQL
and is recommended when Spark is not required.

Initialize the Postgres client
""""""""""""""""""""""""""""""

.. code-block:: python

    from scystream.sdk.database_handling.database_manager import (
        PandasPostgresOperations,
    )

    pg = PandasDatabaseOperations(config)


Write a Pandas DataFrame
""""""""""""""""""""""""

.. code-block:: python

    import pandas as pd

    df = pd.DataFrame([
        {"id": 1, "name": "test"},
        {"id": 2, "name": "test"},
    ])

    pg.write(
        table="test_table",
        data=df,
        mode="overwrite",  # or "append"
    )


Read data from PostgreSQL
""""""""""""""""""""""""

**Option A: Read full table**

.. code-block:: python

    df = pg.read(table="test_table")

**Option B: Use custom query**

.. code-block:: python

    df = pg.read(
        query="SELECT id FROM test_table WHERE id > 1"
    )


Notes
^^^^^

- Table names must not exceed **63 characters** (PostgreSQL limit).
- The SDK will raise an error if this limit is exceeded.
- Supported write modes:
  - ``overwrite`` → replaces table
  - ``append`` → inserts into existing table


Spark Integration
^^^^^^^^^^^^^^^^^

Use Spark when working with large-scale or distributed data processing.

1. Create a Spark session
"""""""""""""""""""""""""

.. code-block:: python

    from scystream.sdk.spark_manager import SparkManager

    manager = SparkManager()


2. Configure PostgreSQL connection
""""""""""""""""""""""""""""""""

.. code-block:: python

    from scystream.sdk.database_handling.postgres_manager import PostgresConfig

    config = PostgresConfig(
        PG_USER="postgres",
        PG_PASS="postgres",
        PG_HOST="postgres",
        PG_PORT=5432,
        DB_NAME="postgres",
    )


3. Setup Postgres integration
"""""""""""""""""""""""""""""

.. code-block:: python

    db = manager.setup_pg(settings)


4. Create a Spark DataFrame
"""""""""""""""""""""""""""

.. code-block:: python

    from pyspark.sql import Row

    spark_df = manager.session.createDataFrame([
        Row(id=1, name="test"),
        Row(id=2, name="test"),
    ])


5. Write data to PostgreSQL
"""""""""""""""""""""""""""

.. code-block:: python

    db.write(
        table="test_table",
        dataframe=spark_df,
        mode="overwrite",
    )


6. Read data from PostgreSQL
""""""""""""""""""""""""""""

**Option A: Read full table**

.. code-block:: python

    df = db.read(table="test_table")

**Option B: Use custom query**

.. code-block:: python

    df = db.read(
        query="SELECT id FROM test_table WHERE id > 1"
    )


Notes
^^^^^

- Spark uses JDBC for communication with PostgreSQL.
- The PostgreSQL driver is automatically included in the SDK.
- Supported write modes:
  - ``overwrite``
  - ``append``
  - ``ignore``
  - ``error``

Summary
^^^^^^^

- Use **PandasPostgresOperations** for simple workflows.
- Use **SparkPostgresOperations** for distributed workloads.
- Use **DatabaseSettings** for environment-based configuration.
- Table names are validated and must comply with PostgreSQL limits.


Using a S3 Bucket
-----------------

The SDK has utilities implemented to up- & download from an S3 Bucket.
Currently, it's *NOT* using Apache Spark for that.

You can interact with an S3 Bucket in **two ways**:

**1. The simple way (no manual connection setup required)**

**2. The advanced way (manual `S3Operations` instantiation)**


Simple Usage
^^^^^^^^^^^^

For most use cases, you can use the new convenience methods that do not require
manually creating a connection object.

Example:

.. code-block:: python
    :emphasize-lines: 4

    from scystream.sdk.file_handling.s3_manager import S3Operations

    @entrypoint()
    def test(settings):
        # Directly download using FileSettings
        S3Operations.download(settings.txt_input, "/tmp/file.txt")

        # Directly upload using FileSettings
        S3Operations.upload(settings.txt_input, "/tmp/file.txt")


Advanced Usage
^^^^^^^^^^^^^^

If you want to reuse the same connection for multiple operations or provide a
custom `S3Config`, you can manually initialize `S3Operations`.

1. Configure the S3 Connection using :class:`scystream.sdk.file_handling.s3_manager.S3Config`
   or :class:`scystream.sdk.env.settings.FileSettings`.

2. Setup the S3 Connection using :class:`scystream.sdk.file_handling.s3_manager.S3Operations`.

3. Use the operations.

Example:

.. code-block:: python
    :emphasize-lines: 5, 12, 14, 20

    from scystream.sdk.file_handling.s3_manager import S3Config, S3Operations

    @entrypoint()
    def test():
        s3_conf = S3Config(
            S3_ACCESS_KEY="access",
            S3_SECRET_KEY="secret",
            S3_HOST="http://localhost",
            S3_PORT="9000"
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

Instead of using `download_file`, you can also use `download_file_from_settings`,
which takes the configurations from a `FileSettings` instance to determine the
`bucket_name` and `s3_object_name`.

