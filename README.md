# scystream-sdk

## Installation

You can install the package via pip once it's published:

```bash
pip install scystream-sdk
```

### Compute Blocks and their configs
One of the central concepts of scystream are the so-called **Compute Blocks**.

A Compute Block describes an independent programm, that acts as some kind of worker
which will be scheduled using the scystream-core application.
This worker executes a task (e.g. a NLP task, a crwaling task).

Each worker can have multiple entrypoints, each aiming to solve one task.
These entrypoints can be configured from the outside using the **Settings**.
These are basically ENV-Variables, which will be parsed & validated using pydantic.

This SDK aims to implement helper functions and other requirements we expect each
Compute Block to have.

To understand the concept of such a Compute Block even more, take a look at the
config below.

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

For now, you have to write this config file on your own. However, at some
point you will be able to generate this config from your code.

To read and validate such a config file you can proceed as follows:

```python3
from scystream.sdk.config.config_loader import load_config 

def main():
    load_config() 

if __name__ == "__main__":
    main()
```

If you want the file to have another name than `cbc.yaml` or you want the file to be 
somewhere else than the root directory you can define that using the parameters the
`load_config` function takes.

Example:

```python3
load_config(config_file_name="test.yaml", config_path="configs/")
```

the `config_path` is the path relative to your root directory

## Basic Usage of the SDK

```python3
from scystream.sdk.core import entrypoint
from scystream.sdk.scheduler import Scheduler


@entrypoint
def example_task():
    print("Executing example_task...")


@entrypoint
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
Therefore you should use the `BaseENVSettings` class.

```python3
from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import BaseENVSettings

class GlobalSettings(BaseENVSettings):
    LANGUAGE: str = "de"

class TopicModellingEntrypointSettings(BaseENVSettings):
    TXT_SRC_PATH: str # if no default provided, setting this ENV manually is a MUST

@entrypoint(TopicModellingEntrypointSettings) # Pass it to the Entrypoint
def topic_modelling(settings):
    print(f"Running topic modelling, using file: {settings.TXT_SRC_PATH}")

@entrypoint
def test_entrypint():
    print("This entrypoint does not have any configs.")
```

We recommend defining your `GlobalSettings` in an extra file and "exporting" the loaded
Settings to make them accessible to other files.
See an example below:

```python3
from scystream.sdk.env.settings import BaseENVSettings

class GlobalSettings(BaseENVSettings):
    LANGUAGE: str = "de"

GLOBAL_SETTINGS = GlobalSettings.load_settings()
```

You can then use the loaded `GLOBAL_SETTINGS` in your other files, by importing them.

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

