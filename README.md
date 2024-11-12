# scystream-sdk

## Installation

You can install the package via pip once it's published:

```bash
pip install scystream-sdk
```

## Introduction

One of the central concepts of scystream are the so-called **Compute Blocks**.

A Compute Block describes an independent programm, that acts as some kind of worker
which will be scheduled using the scystream-core application.
This worker executes a task (e.g. a NLP task, a crawling task).

This SDK aims to provide helper functions and all other requirements you need to implement
a custom Compute Block on your own.

Each worker can have multiple entrypoints, each aiming to solve one task.
These entrypoints can be configured from the outside using the **Settings**.
These are basically ENV-Variables, which will be parsed & validated using pydantic.

You can either set "global" Settings (for the entrypoint), by using the `envs` block.
Or you can set "input/output-related" Settings by using the `config` block in each input/output.

## Basic Usage of the SDK

```python3
from scystream.sdk.core import entrypoint
from scystream.sdk.scheduler import Scheduler


@entrypoint()
def example_task():
    print("Executing example_task...")


@entrypoint()
def another_task(task_name):
    print(f"Executing another_task with task name: {task_name}")


def main():
    Scheduler.list_entrypoints()
    Scheduler.execute_function("example_task")
    Scheduler.execute_function("another_task", "ScheduledTask")


if __name__ == "__main__":
    main()

```

## Defining Settings and Using them.

Earlier, we already wrote about **Settings**.
Each Input & Output can be configured using these settings.
There are also Global Settings, refered to as `envs` in the `cbc.yaml`

Below you can find a simple example of how we define & validate these settings.
Therefore you should use the `EnvSettings` class.

```python3
from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import EnvSettings

class TextDataInputSettings(EnvSettings):
    TXT_SRC_PATH: str # no default provided, manual setting is a MUST

class DBDataInputSettings(EnvSettings):
    DATA_TABLE_NAME: str = "nlp_information"
    DB_HOST: str = "time.rwth-aachen.de"
    DB_PORT: str = 1234

class TopicModellingEntrypointSettings(EnvSettings):
    LANGUAGE: str = "de"
    
    text_data: TextDataInputSettings
    db_data:  DBDataInputSettings

@entrypoint(TopicModellingEntrypointSettings) # Pass it to the Entrypoint
def topic_modelling(settings): # The settings param is automatically injected to your function, you can use it
    print(f"Running topic modelling, using file: {settings.text_data.TXT_SRC_PATH}")

@entrypoint()
def test_entrypint():
    print("This entrypoint does not have any configs.")
```

Of course, you will also be able to use your settings in other files/directories.
For that, just import your desired setting and use the `get_settings()` function.
It will load the configurations correctly.

## Compute Block Config

We expect every repository which will be used within the scystream application
to contain a **Compute Block Config File**, the `cbc.yaml`, within the root directory.
This `cbc.yaml` will be used to define the entrypoints, the inputs & outputs each
Compute Block offers, necessary for the scystream-frontend to understand.

This is an example `cbc.yaml`:

```yaml
name: "NLP toolbox"
description: "Contains NLP algorithms..."
author: "John Doe"
docker_image: "https://ghcr.io/nlp-toolbox"

entrypoints:
  topic_modelling:
    description: "Run topic modelling"
    envs:
      LANGUAGE: "de"
    inputs:
      text_data:
        description: "Text file. Can be uploaded by the user."
        type: "file"
        config:
          TXT_SRC_PATH: null
      db_data:
        description: "Information in a database"
        type: "db_table"
        config:
          DATA_TABLE_NAME: "nlp_information"
          DB_HOST: "time.rwth-aachen.de"
          DB_PORT: 1234
    outputs:
      topic_model:
        type: "file"
        description: "Topic model file"
        config:
          OUTPUT_PATH_TOPIC_MODEL: null
      run_durations:
        type: "db_table"
        description: "Table that contains the run durations per day."
        config:
          RUN_DURATIONS_TABLE_NAME: "run_durations_nlp"

  analyze_runtime:
    description: "Analyze the runtimes"
    inputs:
      run_durations:
        description: "Table that contains all runtimes and dates"
        type: "db_table"
        config:
          RUN_DURATIONS_TABLE_NAME: "run_durations_nlp"
    outputs:
      csv_output:
        type: "file"
        description: "A csv containing statistical information"
        config:
          CSV_OUTPUT_PATH: "outputs/statistics.csv"
```

### Generating a config

After writing the functionality of your ComputeBlock (see more below) you can generate
the corresponding `cbc.yaml` by using the following function:

```python3
from scystream.sdk.config import generate_config_from_compute_block, get_compute_block
from pathlib import Path

@entrypoint()
def example_entrypoint():
    print("Example...")

if __name__ == "__main__":
    compute_block = get_compute_block()
    generate_config_from_compute_block(cb, Path("cbc.yaml"))
```

This will take all the entrypoints, their defined settings, and generate a config from them.

> [!NOTE]
> Make sure to edit the generated config by your user-defined metadata
> (e.g. author, description, docker_image, ...)

### Validating a config

If you want your `cbc.yaml` to be located in a different directory or have a different name, you
have to configure that accordingly:

```python3
from scystream.sdk.config import global_config

if __name__ == "__main__":
    # Set the config_path
    global_config.set_config_path("custom_dir/custom_name.yaml")
```

Of course, you can also write the config completely on your own.

> [!NOTE]
> When using `Scheduler.execute_function("entrypoint")` the Settings for the
> entrypoint and the config will be validated.
> If the Settings do not correspond to the definition in the yaml, execution will not be possible.

To validate the config, you can also use a helper function like this:

```python3
from scystream.sdk.config import validate_config_with_code

@entrypoint()
def example_entrypoint():
    print("Example...")

if __name__ == "__main__":
    validate_config_with_code()
```

## Development of the SDK

### Installation

1. Create a venv and use it

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the package within the venv 

> [!NOTE]
> This will also install all the install_requirements from the setup.py

```bash
pip install -e .
```

3. Develop!

### Tests

To run all the tests run the following command:

```bash
python3 -m unittest discover -s tests
```

