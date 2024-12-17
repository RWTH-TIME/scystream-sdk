import yaml
from typing import Union
from pydantic import ValidationError
from pathlib import Path
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel
from scystream.sdk.config.compute_block_utils import get_compute_block

CONFIG_FILE_DEFAULT_NAME = "cbc.yaml"
UNNAMED_APP_NAME = "unnamed_compute_block"
# In production, the ComputeBlock must be within the same docker network
# as the spark-master & workers!
COMPUTE_BLOCK_SPARK_DEFAULT_MASTER = "spark://spark-master:7077"


class SDKConfig:
    """
    Singleton class that holds the SDK configuration.

    This class manages the configuration for the SDK, primarily the path
    to the configuration file (`cbc.yaml`), the application name, and
    the Spark master URL for ComputeBlock communication.

    :param config_path: Path to the configuration YAML file
        (default: 'cbc.yaml').
    :param app_name: The name of the application
        (default: 'unnamed_compute_block').
    :param cb_spark_master: The URL of the Spark master
        (default: 'spark://spark-master:7077').
    """
    _instance = None

    def __new__(
        cls,
        config_path: str = CONFIG_FILE_DEFAULT_NAME,
        app_name: str = UNNAMED_APP_NAME,
        cb_spark_master: str = COMPUTE_BLOCK_SPARK_DEFAULT_MASTER
    ):
        """
        Creates or returns the singleton instance of SDKConfig.

        :param config_path: Path to the configuration YAML file.
        :param app_name: The name of the application.
        :param cb_spark_master: The URL of the Spark master.

        :return: The singleton SDKConfig instance.
        """
        if cls._instance is None:
            cls._instance = super(SDKConfig, cls).__new__(cls)
            cls._instance.config_path = config_path
            cls._instance.app_name = app_name
            cls._instance.cb_spark_master = cb_spark_master
        return cls._instance

    def set_config_path(self, config_path: str):
        """
        Set the path to the configuration file.

        :param config_path: The path to the configuration YAML file.
        """
        self.config_path = config_path

    def get_config_path(self) -> str:
        """
        Get the path to the configuration file.

        :return: The configuration file path.
        """
        return self.config_path

    def get_cb_spark_master(self) -> str:
        """
        Get the Spark master URL.

        :return: The Spark master URL.
        """
        return self.cb_spark_master

    def set_cb_spark_master(self, spark_master: str) -> str:
        """
        Set the Spark master URL.

        :param spark_master: The spark master URL with this schema:
            spark://url:port
        """


def _compare_configs(
        c1: Union[ComputeBlock, Entrypoint, InputOutputModel],
        c2: Union[ComputeBlock, Entrypoint, InputOutputModel],
        name="block"
):
    """
    Compares two configurations and raises a ValueError if they don't match.

    :param c1: The configuration loaded from the YAML file.
    :param c2: The configuration generated from the code.
    :param name: A descriptive name for the configuration (default: "block").

    :raises ValueError: If the configurations do not match.
    """
    if c1 != c2:
        raise ValueError(
            f"The {name} configs (envs, inputs, outputs) defined\
            in your config YAML do not match the settings defined\
            in your code."
        )


def validate_config_with_code(
        entrypoint_name: str = None
):
    """
    Validates that the configuration loaded from the YAML file matches
    the code-defined configuration for the ComputeBlock.

    :param entrypoint_name: Optional name of an entrypoint to validate.
        If provided, it will validate the specific entrypoint instead of the
        entire ComputeBlock configuration.

    :raises ValueError: If the configurations do not match.
    """
    block_from_cfg = load_config()
    block_from_code = get_compute_block()

    if entrypoint_name:
        _compare_configs(
            block_from_cfg.entrypoints[entrypoint_name],
            block_from_code.entrypoints[entrypoint_name]
        )
    else:
        _compare_configs(block_from_cfg, block_from_code)


def load_config() -> ComputeBlock:
    """
    Loads the configuration from the YAML file and returns a ComputeBlock
    instance.

    Validates the configuration file using Pydantic's model validation.

    :return: A ComputeBlock instance if the YAML file is valid.

    :raises ValueError: If there is a validation error in the configuration
        file.
    """
    try:
        file = _find_and_load_config()
        block_from_cfg = ComputeBlock(**file)
        return block_from_cfg
    except ValidationError as e:
        raise ValueError(f"Configuration file validation error: {e}")


def generate_config_from_compute_block(
    compute_block: ComputeBlock,
    output_path: Path
):
    """
    Generates a YAML configuration file from a ComputeBlock instance.

    Make sure to edit the generated yaml accordingly.

    :param compute_block: The ComputeBlock instance to generate the
        configuration from.
    :param output_path: The path where the YAML configuration file should be
        saved.
    """
    with output_path.open("w") as file:
        yaml.dump(compute_block.model_dump(), file, default_flow_style=False)


def _find_and_load_config():
    """
    Finds and loads the configuration file from the project’s root directory.

    :return: The loaded configuration data as a dictionary.

    :raises FileNotFoundError: If the configuration file is not found.
    :raises ValueError: If there is an error parsing the YAML file.
    """
    sdk_cfg = SDKConfig()
    config_path = sdk_cfg.get_config_path()

    full_path = Path.cwd() / config_path

    if not full_path.is_file():
        raise FileNotFoundError(
            f"Configuration file '{full_path}' not found."
        )

    try:
        with full_path.open("r") as file:
            config_data = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Configuration file '{full_path}' not found.'"
        )
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

    return config_data
