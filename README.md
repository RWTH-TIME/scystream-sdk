# scystream-sdk

## Installation

You can install the package via pip once it's published:

```bash
pip install scystream-sdk
```

## Usage

```python3
from scystream.sdk.core import entrypoint
from scystream.sdk.scheduler import Scheduler
from scystream.sdk.env.settings import BaseENVSettings

class ExampleTaskSettings(BaseENVSettings):
    LANGUAGE: str = "tester123"

@entrypoint(ExampleTaskSettings)
def example_task(settings):
    print(f"The language {settings.LANGUAGE} is currently set in Settings.")
    print("Executing example_task...")

class AnotherTaskSettings(BaseENVSettings):
    TXT_SRC_PATH: str = "test/textdatei.txt"

@entrypoint(AnotherTaskSettings)
def another_task(settings, task_name):
    print(f"Saving a file to {settings.TXT_SRC_PATH}...")
    print(f"Executing another_task with task name: {task_name}")

def main():
    Scheduler.list_entrypoints()
    Scheduler.execute_function("example_task")
    Scheduler.execute_function("another_task", "ScheduledTask")


if __name__ == "__main__":
    main()

```

### Settings

Each entrypoint has so called `Settings` which inherit from `BaseENVSettings`.

These classes are used to define environment variables that the SDK reads and injects
into entrypoint functions.
This is required, as we want to be able to configure the behaviour of the Compute Block entrypoint
to a certain degree from the outside.

In the `cbc.yaml` the SDKs developer defines inputs and outputs of entrypoints (or where these inputs come from).
All of these inputs and outputs have a env_key (read more in the next section).

The Compute Block developer therefore MUST define all of the env_keys he uses in the corresponding 
inputs and outputs as well in the Settings which he passes to the `@entrypoint` decorator.
(TODO: This will be validated)

Of course, the Settings of an entrypoint can also contain ENV-Variables that are not listed
in the inputs/outputs of the `cbc.yaml`. This could make sense if the ComputeBlock developer
wants to use ENV-Variables which will not be changed from the outside.

#### Usage of Settings elsewhere

As just described, usage of Settings when defining the entrypoints is mandatory.

Howerver when using Settings elsewhere you can import your `YourCustomSettings` class
(that inherits from `BaseENVSettings`) and load and validate the variables using

```python3
from wherever import YourCustomSettings

custom_settings = YourCustomSettings.load_settings()
```

### Compute Block Config Files
We expect every repository which will be used within the scystream application
to contain a `Compute Block Config File`, the `cbc.yaml`, within the root directory.

This yaml-file describes the compute block itself.
It shows the entrypoints, their inputs and outputs.

This is an example `cbc.yaml`:

```yaml
name: "NLP toolbox"
description: "Contains NLP algorithms..."
author: "John Doe"
docker_image: "https://ghcr.io/nlp-toolbox"

entrypoints:
  topic_modelling:
    description: "Run topic modelling"
    inputs:
      language:
        description: "The language to use"
        type: "env"
        env_key: "LANG"
        optional: True
        default_value: "de" 
      text_data:
        description: "Text file. Can be uploaded by the user."
        type: "file"
        env_key: "TXT_SRC_PATH"
        optional: False
      db_data:
        description: "Information in a database"
        type: "db_table"
        env_key: "DATA_TABLE_NAME"
        table_name: "nlp_information"
        optional: True
    outputs:
      topic_model:
        type: "file"
        description: "Topic model file"
        env_key: "OUTPUT_PATH_TOPIC_MODEL"
        file_path: "outputs/output.pkl"
      run_durations:
        type: "db_table"
        description: "Table that contains the run durations per day."
        env_key: "RUN_DURATIONS_TABLE_NAME"
        table_name: "run_durations_nlp"

  analyze_runtime:
    description: "Analyze the runtimes"
    inputs:
      run_durations:
        type: "db_table"
        env_key: "RUN_DURATIONS_TABLE_NAME"
        table_name: "run_durations_nlp"
        optional: True
    outputs:
      csv_output:
        type: "file"
        description: "A csv containing statistical information"
        env_key: "CSV_OUTPUT_PATH"
        file_path: "outputs/statistics.csv"
```

To read and validate such a config file u can proceed as follows:

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


## Development of the SDK

### Installation

1. Create a venv

```bash
python3 -m venv .venv
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

