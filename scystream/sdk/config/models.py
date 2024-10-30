from typing import Optional, Dict, Literal
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


class InputOutputDefinitions(BaseModel):
    type: DataTypes
    description: Optional[StrictStr] = None
    item_type: Optional[DataTypes] = Field(
        None, description="Type of items in the list")
    table_name: Optional[StrictStr] = Field(
        None, description="Name of the spark_table,\
                required if type is spark_table", validate_default=True)
    # TODO: Add an optional example field, this could be very helpful for the
    # frontend

    """
    If the type is spark_table, table_name must also be set
    """
    @field_validator("table_name")
    def validate_table_name(cls, v, info):
        set_type = info.data.get("type")
        if set_type == "spark_table":
            if not v:
                raise ValueError(
                    "table_name must be set when type is 'spark_table'")
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
