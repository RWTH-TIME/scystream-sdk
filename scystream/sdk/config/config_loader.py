import yaml
from typing import Union
from pydantic import ValidationError
from pathlib import Path
from .models import ComputeBlock

CONFIG_FILE_DEFAULT_NAME = "cbc.yaml"


def _remove_empty_dicts(data):
    """
    Remove keys with empty dictionaries from a nested structure.
    """
    if isinstance(data, dict):
        return {k: _remove_empty_dicts(v) for k, v in data.items() if v != {}}
    elif isinstance(data, list):
        return [_remove_empty_dicts(i) for i in data]
    else:
        return data


def load_config(
    config_file_name: str = CONFIG_FILE_DEFAULT_NAME,
    config_path: Union[str, Path] = None
) -> ComputeBlock:
    """
    Returns and Validates the Compute Block YAML definition.
    Returns a ComputeBlock instance if the validation is successfull
    """
    try:
        file = _find_and_load_config(config_file_name, config_path)
        block = ComputeBlock(**file)
        # TODO: Check if envs && input/output configs correspond to the
        # loaded one
        return block
    except ValidationError as e:
        raise ValueError(f"Configuration file validation error: {e}")


def generate_yaml_from_compute_block(
    compute_block: ComputeBlock,
    output_path: Path
):
    cleaned_data = _remove_empty_dicts(compute_block.dict())
    with output_path.open("w") as file:
        yaml.dump(cleaned_data, file, default_flow_style=False)


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
