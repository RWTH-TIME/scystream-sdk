import yaml
from typing import Union
from pydantic import ValidationError
from pathlib import Path
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel
from scystream.sdk.config.compute_block_utils import get_compute_block

CONFIG_FILE_DEFAULT_NAME = "cbc.yaml"
UNNAMED_APP_NAME = "unnamed_compute_block"
# TODO: is that right? Is ComputeBlock in Docker Network?
COMPUTE_BLOCK_SPARK_DEFAULT_MASTER = "spark://spark-master:7077"


class SDKConfig:
    """
    This is a singleton class that holds the configuration of
    the sdk.
    For now, it only holds the config_path which points to
    the cbc.yaml.
    """
    _instance = None

    def __new__(
        cls,
        config_path: str = CONFIG_FILE_DEFAULT_NAME,
        app_name: str = UNNAMED_APP_NAME,
        cb_spark_master: str = COMPUTE_BLOCK_SPARK_DEFAULT_MASTER
    ):
        if cls._instance is None:
            cls._instance = super(SDKConfig, cls).__new__(cls)
            cls._instance.config_path = config_path
            cls._instance.app_name = app_name
            cls._instance.cb_spark_master = cb_spark_master
        return cls._instance

    def set_config_path(self, config_path: str):
        self.config_path = config_path

    def get_config_path(self) -> str:
        return self.config_path


def _compare_configs(
        config_from_yaml: Union[ComputeBlock, Entrypoint, InputOutputModel],
        config_from_code: Union[ComputeBlock, Entrypoint, InputOutputModel],
        name="block"
):
    """
    Compares two configurations and raises a ValueError if they don't match.
    """
    if config_from_yaml != config_from_code:
        raise ValueError(
            f"The {name} configs (envs, inputs, outputs) defined\
            in your config YAML do not match the settings defined\
            in your code."
        )


def validate_config_with_code(
        entrypoint_name: str = None
):
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
    Returns the Compute Block defined by the passed yaml.
    Returns a ComputeBlock instance if the syntax-validation is successfull
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
    with output_path.open("w") as file:
        yaml.dump(compute_block.model_dump(), file, default_flow_style=False)


def _find_and_load_config():
    """
    Loads the compute block config YAML from the projects root directory
    returns the loaded file
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
