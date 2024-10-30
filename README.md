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

### Compute Block Config Files
We expect every repository which will be used within the scystream application
to contain a `Compute Block Config File`, the `cbc.yaml`, within the root directory.

This yaml-file describes the compute block itself.
It shows the entrypoints, their inputs and outputs.

This is an example `cbc.yaml`:

```yaml
name: "The first Web-Crawler"
description: "This is a web crawler, it crawls text..."
author: "John Doe"

entrypoints:
  crawl:
    description: "Crawl text from specified URLs"
    inputs:
      url_list:
        type: "list"
        item_type: "string"
        description: "List of URLs to crawl. Can be defined by the user."
    outputs:
      text_data:
        type: "spark_table"
        description: "Crawled text data in a spark table"
        table_name: "text_data_spark"

  analyze_url:
    description: "Analyzes if data is crawlable"
    inputs:
      url-list:
        type: "list"
        item_type: "string"
        description: "List of URLS to check"
    outputs:
      was_sucess:
        type: "bool"
        description: "True if all urls can be crawled"
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

> [!INFO]
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

