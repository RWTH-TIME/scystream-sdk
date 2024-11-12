import yaml
from typing import Union
from pydantic import ValidationError
from pathlib import Path
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel
from scystream.sdk.config.compute_block_utils import get_compute_block

CONFIG_FILE_DEFAULT_NAME = "cbc.yaml"


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
        config_file_name: str = CONFIG_FILE_DEFAULT_NAME,
        config_path: Union[str, Path] = None,
        entrypoint_name: str = None
):
    block_from_cfg = load_config(config_file_name, config_path)
    block_from_code = get_compute_block()

    if entrypoint_name:
        _compare_configs(
            block_from_cfg.entrypoints[entrypoint_name],
            block_from_code.entrypoints[entrypoint_name]
        )
    else:
        _compare_configs(block_from_cfg, block_from_code)


def load_config(
    config_file_name: str = CONFIG_FILE_DEFAULT_NAME,
    config_path: Union[str, Path] = None,
) -> ComputeBlock:
    """
    Returns the Compute Block defined by the passed yaml.
    Returns a ComputeBlock instance if the syntax-validation is successfull
    """
    try:
        file = _find_and_load_config(config_file_name, config_path)
        block_from_cfg = ComputeBlock(**file)
        return block_from_cfg
    except ValidationError as e:
        raise ValueError(f"Configuration file validation error: {e}")


def generate_config_from_compute_block(
    compute_block: ComputeBlock,
    output_path: Path
):
    with output_path.open("w") as file:
        yaml.dump(compute_block.dict(), file, default_flow_style=False)


def _find_and_load_config(
        config_file_name: str,
        config_path: Union[str, Path] = None
):
    """
    Loads the compute block config YAML from the projects root directory
    returns the loaded file
    """
    base_path = Path.cwd()
    if config_path:
        base_path /= Path(config_path)

    full_path = base_path / config_file_name

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
