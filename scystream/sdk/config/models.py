from typing import Optional, Dict, Literal
from pydantic import BaseModel, StrictStr, field_validator, Field

FILE_TYPE_IDENTIFIER = "file"
DB_TABLE_TYPE_IDENTIFIER = "db_table"

"""
This file contains the schema definition for the config file.
"""


class InputOutputModel(BaseModel):
    type: Literal[FILE_TYPE_IDENTIFIER, DB_TABLE_TYPE_IDENTIFIER]
    description: Optional[StrictStr] = None
    config: Optional[Dict[StrictStr, Optional[StrictStr]]] = Field(
        default=None,
        description="The configuration for the input values\
                (file_path, table_name, etc.)"
    )


class Entrypoint(BaseModel):
    description: StrictStr
    envs: Optional[Dict[StrictStr, StrictStr]] = None
    inputs: Dict[StrictStr, InputOutputModel]
    outputs: Dict[StrictStr, InputOutputModel]


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
