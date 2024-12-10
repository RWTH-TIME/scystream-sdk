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


// TODO: generate config
// TODO: validate config
// TODO: file upload & database usage -> Spark Usage


