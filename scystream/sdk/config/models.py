from typing import Optional, Dict, Literal, Any, Callable
from pydantic import BaseModel, StrictStr, field_validator, Field

"""
This file contains the schema definition for the config file.
"""

STRING_TYPE = "string"
INT_TYPE = "int"
FLOAT_TYPE = "float"
BOOL_TYPE = "bool"
LIST_TYPE = "list"
SPARK_TABLE_TYPE = "spark_table"

DataTypes = Literal[STRING_TYPE, INT_TYPE, FLOAT_TYPE,
                    BOOL_TYPE, LIST_TYPE, SPARK_TABLE_TYPE]

VALIDATORS: Dict[DataTypes, Callable[[Any], bool]] = {
    STRING_TYPE: lambda v: isinstance(v, str),
    INT_TYPE: lambda v: isinstance(v, str),
    FLOAT_TYPE: lambda v: isinstance(v, float),
    BOOL_TYPE: lambda v: isinstance(v, bool),
    LIST_TYPE: lambda v: isinstance(v, list),
    # SPARK_TABLE_TYPE should be the name of the spark table (str)
    SPARK_TABLE_TYPE: lambda v: isinstance(v, str)
}


class BaseIOModel(BaseModel):
    type: DataTypes
    description: Optional[StrictStr] = None


class InputDefinitions(BaseIOModel):
    optional: bool
    default_value: Optional[Any] = Field(default=None, validate_default=True)

    @field_validator("default_value")
    def validate_default_value(cls, v, info):
        optional = info.data.get("optional")
        expected_type = info.data.get("type")

        if not optional:
            # If field is not optional, default_value does not have to be set
            return v

        if v is None:
            raise ValueError("default_value must be set when optional is True")

        validator = VALIDATORS.get(expected_type)
        if validator and not validator(v):
            raise TypeError(f"default_value must be of type {expected_type}")

        return v


class OutputDefinitions(BaseIOModel):
    pass


class Entrypoint(BaseModel):
    description: StrictStr
    inputs: Dict[StrictStr, InputDefinitions]
    outputs: Dict[StrictStr, OutputDefinitions]


class ComputeBlock(BaseModel):
    name: StrictStr
    description: StrictStr
    author: StrictStr
    entrypoints: Dict[StrictStr, Entrypoint]
    docker_image: Optional[StrictStr]

    @field_validator("entrypoints")
    def check_entrypoints(cls, v):
        if not v:
            raise ValueError("At least one entrypoint must be defined.")
        return v
