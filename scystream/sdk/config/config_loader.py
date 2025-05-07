import yaml
from typing import Union
from pydantic import ValidationError
from pathlib import Path
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel
from scystream.sdk.config.compute_block_utils import get_compute_block

CBC_CONFIG_DEFAULT_IDENTIFIER = "cbc.yaml"
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

    :param app_name: The name of the application
        (default: 'unnamed_compute_block').
    :param cb_spark_master: The URL of the Spark master
        (default: 'spark://spark-master:7077').
    """
    _instance = None

    def __new__(
        cls,
        app_name: str = UNNAMED_APP_NAME,
        cb_spark_master: str = COMPUTE_BLOCK_SPARK_DEFAULT_MASTER
    ):
        """
        Creates or returns the singleton instance of SDKConfig.

        :param app_name: The name of the application.
        :param cb_spark_master: The URL of the Spark master.

        :return: The singleton SDKConfig instance.
        """
        if cls._instance is None:
            cls._instance = super(SDKConfig, cls).__new__(cls)
            cls._instance.app_name = app_name
            cls._instance.cb_spark_master = cb_spark_master
        return cls._instance

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
        entrypoint_name: str | None = None,
        config_path: str | None = None
):
    """
    Validates that the configuration loaded from the YAML file matches
    the code-defined configuration for the ComputeBlock.

    :param entrypoint_name: Optional name of an entrypoint to validate.
        If provided, it will validate the specific entrypoint instead of the
        entire ComputeBlock configuration.

    :raises ValueError: If the configurations do not match.
    """
    block_from_cfg = load_config(config_path)
    block_from_code = get_compute_block()

    if entrypoint_name:
        _compare_configs(
            block_from_cfg.entrypoints[entrypoint_name],
            block_from_code.entrypoints[entrypoint_name]
        )
    else:
        _compare_configs(block_from_cfg, block_from_code)


def load_config(path_to_cfg: str | None) -> ComputeBlock:
    """
    Loads and validates configuration from a YAML file.

    If no path is provided, attempts to load from the default location in the
    current working directory.

    :param path_to_cfg: Optional path to the configuration YAML file.
    :return: A ComputeBlock instance if the YAML is valid.
    :raises ValueError: If the config file is missing, invalid, or fails
        validation.
    """
    try:
        if path_to_cfg:
            path = Path(path_to_cfg)
        else:
            path = Path.cwd() / CBC_CONFIG_DEFAULT_IDENTIFIER

        if not path.is_file():
            raise FileNotFoundError(f"Configuration file '{path}' not found.")

        with path.open("r") as f:
            config_data = yaml.safe_load(f)

        return ComputeBlock(**config_data)

    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")
    except ValidationError as e:
        raise ValueError(f"Configuration validation error: {e}")


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
