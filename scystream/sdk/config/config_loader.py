import yaml
from typing import Optional, Dict, Literal, Any, Callable
from pydantic import BaseModel, StrictStr, field_validator, Field
import os

"""
This file contains the schema definition, the read function and validation
for the config file.
"""

PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

print(PROJECT_ROOT_DIR)

STRING_TYPE = "string"
INT_TYPE = "int"
FLOAT_TYPE = "float"
BOOL_TYPE = "bool"
LIST_TYPE = "list"
SPARK_TABLE_TYPE = "spark_table"

CONFIG_FILE_DEFAULT_NAME = "cbc.yaml"

DataTypes = Literal[STRING_TYPE, INT_TYPE, FLOAT_TYPE,
                    BOOL_TYPE, LIST_TYPE, SPARK_TABLE_TYPE]

VALIDATORS: Dict[str, Callable[[Any], bool]] = {
    "string": lambda x: isinstance(x, str),
    "int": lambda x: isinstance(x, (int)),
    "number": lambda x: isinstance(x, (float)),
    "bool": lambda x: isinstance(x, (bool)),
    "list": lambda x: isinstance(x, (list)),
    # spark_table must be of type str
    "spark_table": lambda x: isinstance(x, (str))
}


class InputOutputDefinitions(BaseModel):
    type: DataTypes
    description: Optional[StrictStr] = None
    item_type: Optional[DataTypes] = Field(
        None, description="Type of items in the list")
    table_name: Optional[StrictStr] = Field(
        None, description="Name of the spark_table,\
                required if type is spark_table")
    example: Optional[DataTypes] = Field(
        None, description="Example for the Input/Output"
    )

    """
    If the type is spark_table, table_name must also be set
    """
    @field_validator("table_name")
    def validate_table_name(cls, v, values):
        set_type = values.get("type")
        if set_type == "spark_table":
            if not v:
                raise ValueError(
                    "table_name must be set when type is 'spark_table'")
        return v

    """
    Check if the example corresponds with the inputs type
    """
    @field_validator("example")
    def validate_example_type(cls, v, values):
        expected_type = values.get("type")

        if expected_type in VALIDATORS:
            if not VALIDATORS[expected_type](v):
                raise ValueError(f"Example must be of type \
                        '{expected_type}' when type is '{expected_type}'")

        return v


class Entrypoint(BaseModel):
    description: StrictStr
    inputs: Dict[StrictStr, InputOutputDefinitions]
    outputs: Dict[StrictStr, InputOutputDefinitions]


class ComputeBlock(BaseModel):
    name: StrictStr
    description: StrictStr
    author: StrictStr
    entrypoints: Dict[StrictStr, Entrypoint]

    @field_validator("entrypoints")
    def check_entrypoints(cls, v):
        if not v:
            raise ValueError("At least one entrypoint must be defined.")
        return v


def validate_config(config_path: str = CONFIG_FILE_DEFAULT_NAME) -> bool:
    """
    Reads the passed Compute Block YAML definition.
    Returns True if the validation using pydantic was successfull
    """


def load_config(config_path: str = CONFIG_FILE_DEFAULT_NAME) -> ComputeBlock:
    """
    Loads a YAML configuration file for workflow unit definitions.
    """

    root_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(root_dir, "..", config_path)

    with open(full_path, "r") as file:
        config = yaml.safe_load(file)

    return ComputeBlock(**config)
