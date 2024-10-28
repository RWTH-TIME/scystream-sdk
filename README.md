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

### Development

1. Create a venv

```bash
python3 -m venv .venv
```

2. Install the package within the venv 

> [!INFO]
> This will also install all the install_requirements from the setup.py

```bash
pip install -e .[dev]
```

3. Develop!
