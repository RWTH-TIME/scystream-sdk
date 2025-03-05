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

Find the whole Documentation [here](https://docs-scystream.go.iso.rwth-aachen.de/)!

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

3. Install the dev dependencies

```bash
pip install -e ".[dev]"
```

4. Develop!

### Tests

To run all the tests run the following command:

```bash
python3 -m unittest discover -s tests
```

