from typing import Optional, Dict, Literal, Union
from pydantic import BaseModel, StrictStr, field_validator, Field

"""
This file contains the schema definition for the config file.
"""


class BaseInputModel(BaseModel):
    description: Optional[StrictStr] = None
    optional: bool = False
    env_key: Optional[StrictStr] = Field(
        default=None, validate_default=True,
        description="The env_key describes the key of the environment variable\
                which can be set to override the default value"
    )

    @field_validator("env_key")
    def validate_env_key(cls, v, info):
        """a
        If optional == False, the env_key must be set! As the user must have
        the possibility to define the variable.
        """
        optional = info.data.get("optional")

        if not optional and v is None:
            raise ValueError("If optional is False, the env_key must be set.")

        return v


class EnvInput(BaseInputModel):
    """
    The EnvInput type describes the input of an ENV variable
    It should describe one env-variable the compute unit accesses.

    The default_value can be overridden, if the env_key is set.
    """
    type: Literal["env"]
    default_value: Optional[StrictStr] = Field(
        default=None, validate_default=True)

    @field_validator("default_value")
    def validate_default_value(cls, v, info):
        """
        If optional == True, default_value must be set!
        """
        optional = info.data.get("optional")

        if optional and v is None:
            raise ValueError("If optional is True, default_value must be set.")

        return v


class FileInput(BaseInputModel):
    """
    The FileInput type describes the input for files.
    The file_path describes the path to a file on the S3 bucket,
    it can be overriden by using the env_key, if set.

    This makes sense, if a user should be able to manually upload
    files the compute units wants to access. It does not know the
    path to the file while writing the defintion.
    """
    type: Literal["file"]
    file_path: Optional[StrictStr] = Field(
        default=None, validate_default=True,
        description="The default value of the FileInput type.\
                Can be overriden."
    )

    @field_validator("file_path")
    def validate_file_path(cls, v, info):
        """
        If optional == True, file_path must be set!
        """

        optional = info.data.get("optional")

        if optional and v is None:
            raise ValueError("If optional is True, file_path must be set.")


class BaseOutputModel(BaseModel):
    description: StrictStr
    env_key: StrictStr = Field(
        description="The env_key describes the key of the environment variable\
                which can be set to override the default value"
    )


class FileOutput(BaseOutputModel):
    """
    The FileOutput type describes the output of a file.
    The file_path describes the path to a file on the S3 bucket.
    """
    type: Literal["file"]
    file_path: StrictStr = Field(
        desscription="The path to the file on the S3 bucket."
    )


class DBTableOutput(BaseOutputModel):
    """
    The DBTableOutput type defines a table that provides output data.
    The table_name refers to the output table name.
    """
    type: Literal["db_table"]
    table_name: StrictStr = Field(
        description="The name of the output database table."
    )


class DBTableInput(BaseInputModel):
    """
    The DBTableInput type defines a table that provides input data.
    The table_name can be overriden by using the env_key, if set.

    This makes sense, if a previous compute units output db_table should
    be used as an input. This table_name is then not known while writing the
    definition.
    """
    type: Literal["db_table"]
    table_name: Optional[StrictStr] = Field(
        default=None, validate_default=True,
        description="The default value of the DBTableInput type.\
                Can be overriden."
    )

    @field_validator("table_name")
    def validate_table_name(cls, v, info):
        """
        If optional == True, table_name must be set!
        """

        optional = info.data.get("optional")

        if optional and v is None:
            raise ValueError("If optional is True, table_name must be set.")


class Entrypoint(BaseModel):
    description: StrictStr
    inputs: Dict[StrictStr, Union[EnvInput, FileInput, DBTableInput]]
    outputs: Dict[StrictStr, Union[FileInput, DBTableOutput]]


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
