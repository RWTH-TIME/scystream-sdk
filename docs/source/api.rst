API Reference
=============

This page provides an overview of all public objects, functions, and methods included in the scystream-sdk.

Core (:mod:`scystream.sdk.core`)
----------------------------------
The core of the SDK are entrypoints

To configure entrypoints a decorator is provided. Use this to define entrypoints, and pass :class:`scystream.sdk.env.settings.EnvSettings` if necessary.

* :meth:`scystream.sdk.core.entrypoint`: Decorator for defining entrypoints.


Config (:mod:`scystream.sdk.config`)
-------------------------------------
The scystream-sdk contains of two main configuration objects.

1. SDKConfig (:class:`scystream.sdk.config.SDKConfig`)
    This is a Object containing all the global configurations for the SDK to work.
    This could be, for example, the app name, which will be used to identify the compute block on your spark-master.

2. ComputeBlockConfig (:class:`scystream.sdk.config.models.ComputeBlock`)
    The ComputeBlockConfig is a file that "configures" the ComputeBlocks Inputs and Outputs.
    It also contains some metadata configurations (e.g. Author, Docker-Image-URL, ...).

        * :meth:`scystream.sdk.config.load_config`: loads the configuration from the yaml file and returns a ComputeBlock instance.
        * :meth:`scystream.sdk.config.validate_config_with_code`: can be used to validate the definition of an entrypoint in the compute block config yaml with the actual definition within the appliation code
        * :meth:`scystream.sdk.config.config_loader.generate_config_from_compute_block`: generates a compute block config file from .
        * :meth:`scystream.sdk.config.get_compute_block`: converts the entrypoints and settings defined in the code into a  `scystream.sdk.config.models.ComputeBlock` instance.


ENVs and Settings (:mod:`scystream.sdk.env`)
--------------------------------------------
When using the scystream-sdk and defining entrypoints, its important to give the user (via the scheduler) the possibility
to define settings for each entrypoints.

These settings are set using env variables.

There are three main types of Settings:

1. EnvSettings (:class:`scystream.sdk.env.settings.EnvSettings`)
    The EnvSettings class inherits from the pydantic `BaseSettings` class. It can be used to parse env-variables from the .env file.
    You should use this class when defining the Settings for an entrypoint.

    However, you can also use this function to parse your custom environment variables which might not be user-defined.

2. InputSettings (:class:`scystream.sdk.env.settings.InputSettings`)
    Use this when defining settings for your inputs.
    Under the hood, this works exactly the same as EnvSettings.

3. OutputSettings (:class:`scystream.sdk.env.settings.OutputSettings`)
    Use this when defining settings for your outputs.
    Under the hood, htis works exactly the same as EnvSettings.

The SDK also provides more specific types of inputs and outputs. These offer predefined config-keys:

4. FileSettings (:class:`scystream.sdk.env.settings.FileSettings`)

5. DatabaseSettings (:class:`scystream.sdk.env.settings.DatabaseSettings`)

Spark Manager (:mod:`scystream.sdk.spark_manager`)
--------------------------------------------------
We aim to handle all our data exchange & data usage using Apache Spark.

To use Spark you need to configure the :class:`scystream.sdk.spark_manager.SparkManager`, which
connects to a spark-master and gives you access to the session.

Bare in mind, currently only the database connection is handled using Spark. When using a
Database, please make sure to setup the connection using:

* :meth:`scystream.sdk.spark_manager.SparkManager.setup_pg`: Setups connection, returns a :class:`scystream.sdk.database_handling.database_manager.SparkDatabaseOperations` instance.


Database Handling (:mod:`scystream.sdk.database_handling`)
-----------------------------------------------------------

The database handling package provides utilities to connect to and interact
with databases using a unified interface.

It supports both **Pandas-based** and **Apache Spark-based** workflows.

Supported Databases
^^^^^^^^^^^^^^^^^^^

The SDK supports all databases compatible with SQLAlchemy via a DSN
(Data Source Name), including:

- PostgreSQL
- MySQL
- SQLite
- Snowflake
- and others

Core Functionality
^^^^^^^^^^^^^^^^^^

The :mod:`scystream.sdk.database_handling.database_manager` module provides
the following core abstractions:

- :class:`scystream.sdk.database_handling.database_manager.BaseDatabaseOperations`
- :meth:`scystream.sdk.database_handling.database_manager.BaseDatabaseOperations.read`
- :meth:`scystream.sdk.database_handling.database_manager.BaseDatabaseOperations.write`

These methods allow reading from and writing to a database using a consistent API.

Pandas Integration
^^^^^^^^^^^^^^^^^^

For most use cases, the SDK provides a Pandas-based implementation:

- :class:`scystream.sdk.database_handling.database_manager.PandasDatabaseOperations`

This implementation uses SQLAlchemy and supports any DSN-compatible database.

Spark Integration
^^^^^^^^^^^^^^^^^

For distributed workloads, the SDK provides a Spark-based implementation:

- :class:`scystream.sdk.database_handling.database_manager.SparkDatabaseOperations`

.. note::

   Currently, Spark integration only supports **PostgreSQL**.

To initialize Spark database access, use:

.. code-block:: python

    from scystream.sdk.spark_manager import SparkManager

    manager = SparkManager()
    db = manager.setup_pg(dsn)

File Handling (:mod:`scystream.sdk.file_handling`)
------------------------------------------------------
The file handling package contains all the required utilities to connect & query from/to a file storage.
Currently the file handling package does NOT make use of Apache Spark.

Currently the scystream-sdk supports the following file-storages:

1. S3 Buckets (:mod:`scystream.sdk.file_handling.s3_manager`)
    The `s3_manager` module currently supports:

        * :class:`scystream.sdk.file_handling.s3_manager.S3Config`: must be used to configure a connection to a s3 bucket.
        * :meth:`scystream.sdk.file_handling.s3_manager.S3Operations.upload_file`: can be used to upload a file to the s3 bucket.
        * :meth:`scystream.sdk.file_handling.s3_manager.S3Operations.download_file`: can be used to download a file from the s3 bucket.

Scheduler (:mod:`scystream.sdk.scheduler`)
------------------------------------------
The scheduler module can be used to list & execute entrypoints.

* :meth:`scystream.sdk.scheduler.Scheduler.execute_function`: validates the entrypoint with the entrypoint defined in the config yaml. If valid, executes it.
* :meth:`scystream.sdk.scheduler.Scheduler.list_entrypoints`: lists all the registered entrypoints in the application.


Modules
-------

The following modules are part of the `scystream-sdk`:

.. toctree::
   :maxdepth: 2
   :caption: Modules

   scystream.sdk
   scystream.sdk.config
   scystream.sdk.env
   scystream.sdk.database_handling
   scystream.sdk.file_handling
