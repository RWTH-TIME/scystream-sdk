from typing import Optional, Dict, Literal, Union, List
from pydantic import BaseModel, StrictStr, field_validator, Field, \
    StrictInt, StrictFloat

FILE_TYPE_IDENTIFIER = "file"
PG_TABLE_TYPE_IDENTIFIER = "pg_table"
CUSTOM_TYPE_IDENTIFIER = "custom"


class InputOutputModel(BaseModel):
    """
    Represents configuration for inputs or outputs in a ComputeBlock.

    The configuration is defined as a dictionary with key-value pairs, where:

    - The key is the name of an environment variable (e.g., `FILE_PATH`,
      `TABLE_NAME`).

    - The value is the default value for that environment variable, which can
      be a string, integer, or float.

    If a value is explicitly set to `null`, validation will fail unless the
    environment variable is manually set by the ComputeBlock user.

    :param type: Type of the I/O (file, db_table, TODO: SetType).
    :param description: A description of the I/O.
    :param config: A dictionary of configuration settings for
        the I/O, such as file path, table name, etc.
    """
    type: Literal[FILE_TYPE_IDENTIFIER,
                  PG_TABLE_TYPE_IDENTIFIER, CUSTOM_TYPE_IDENTIFIER]
    description: Optional[StrictStr] = None
    config: Optional[
        Dict[
            StrictStr,
            Optional[Union[StrictStr, StrictInt, StrictFloat, List, bool]]
        ]] = Field(
            default=None,
            description="The configuration for the input values\
                (file_path, table_name, etc.)"
    )

    def __eq__(self, other):
        """
        Compares the configuration keys only, as other attributes
        are not relevant for determining equality at this stage.
        """
        if isinstance(other, InputOutputModel):
            return (
                self._sorted_config() == other._sorted_config()
            )
        return False

    def _sorted_config(self):
        """
        Sorts the configuration dictionary by key for consistent comparison.
        """
        return dict(sorted(self.config.items() if self.config else {}))


class Entrypoint(BaseModel):
    """
    Represents an entrypoint within a ComputeBlock.

    An entrypoint includes:
    - A description of the entrypoint's purpose.

    - A dictionary of environment variables (`envs`), where each key-value
      pair represents an environment variable and its default value.
    - These variables should be shared across the entrypoint.

    - Input and output configurations, each described by the InputOutputModel.

    If an environment variable’s value is set to `None` in the configuration,
    the ComputeBlock user must provide that variable during runtime, or else
    the process will fail.

    :param description: A description of the entrypoint.
    :param envs: A dictionary of environment variables w  their default
        values.
    :param inputs: A dictionary of input configurations.
    :param outputs: A dictionary of output configurations.
    """
    description: StrictStr
    envs: Optional[
        Dict[
            StrictStr,
            Optional[Union[StrictStr, StrictInt, StrictFloat, List, bool]]
        ]
    ] = None
    inputs: Optional[Dict[StrictStr, InputOutputModel]] = None
    outputs: Optional[Dict[StrictStr, InputOutputModel]] = None

    def __eq__(self, other):
        """
        Compares the `envs`, `inputs`, and `outputs` only, as other
        attributes are not relevant for determining equality at this stage.
        """
        if isinstance(other, Entrypoint):
            return (
                self._sorted_envs() == other._sorted_envs() and
                self._sorted_inputs() == other._sorted_inputs() and
                self._sorted_outputs() == other._sorted_outputs()
            )
        return False

    def _sorted_envs(self):
        return dict(sorted(self.envs.items()) if self.envs else {})

    def _sorted_inputs(self):
        return dict(sorted(self.inputs.items()) if self.inputs else {})

    def _sorted_outputs(self):
        return dict(sorted(self.outputs.items()) if self.outputs else {})


class ComputeBlock(BaseModel):
    """
    Represents a ComputeBlock configuration, which describes the compute
    process, including entrypoints, inputs, and outputs.

    A ComputeBlock is defined by:

    - A name, description, and author.

    - One or more entrypoints that specify how data is passed into and out
      of the compute process.

    - Optionally, a Docker image to specify the execution environment.

    At least one entrypoint must be defined for the ComputeBlock to be valid.

    :param name: The name of the ComputeBlock.
    :param description: A description of the ComputeBlock.
    :param author: The author of the ComputeBlock.
    :param entrypoints: A dictionary of entrypoints.
    :param docker_image: The Docker image for the execution
            environment, if any.
    """
    name: StrictStr
    description: StrictStr
    author: StrictStr
    entrypoints: Dict[StrictStr, Entrypoint]
    docker_image: Optional[StrictStr]

    @field_validator("entrypoints")
    def check_entrypoints(cls, v):
        """
        Validates that at least one entrypoint is defined for the ComputeBlock.

        Raises:
            ValueError: If no entrypoints are defined.
        """
        if not v:
            raise ValueError("At least one entrypoint must be defined.")
        return v

    def __eq__(self, other):
        """
        Compares the entrypoints only, as other attributes
        are not relevant for determining equality at this stage.
        """

        if isinstance(other, ComputeBlock):
            return (
                self._sorted_entrypoints() == other._sorted_entrypoints()
            )
        return False

    def _sorted_entrypoints(self):
        return {key: value for key, value in sorted(self.entrypoints.items())}
