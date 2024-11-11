import functools
from typing import Callable, Type, Optional, Union
from .env.settings import EnvSettings
from pydantic import ValidationError
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel
from pydantic_core import PydanticUndefinedType
from scystream.sdk.env.settings import InputSettings, OutputSettings

_registered_functions = {}


def entrypoint(settings_class: Optional[Type[EnvSettings]] = None):
    """
    Decorator to mark a function as an entrypoint.
    It also loads and injects the settings of the entrypoint.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if settings_class is not None:
                # Load settings
                try:
                    # TODO: 1. LoadSettings
                    # TODO: 2. Generate config from settings (only for the entrypoint)
                    # TODO: 3. Validate if generated config and given config are same
                    settings = settings_class.get_settings()
                except ValidationError as e:
                    raise ValueError(f"Invalid environment configuration: {e}")

                return func(settings, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        _registered_functions[func.__name__] = {
            "function": wrapper,
            "settings": settings_class
        }
        return wrapper
    return decorator


def get_registered_functions():
    """Returns a dictionary of registered entrypoint functions."""
    print(_registered_functions)
    return _registered_functions


def _get_pydantic_default_value_or_none(value):
    if type(value.default) is PydanticUndefinedType:
        return None
    return value.default


def _build_input_output_dict_from_class(
    subject: Union[InputSettings, OutputSettings]
):
    config_dict = {}
    for key, value in subject.model_fields.items():
        config_dict[key] = _get_pydantic_default_value_or_none(value)
    return InputOutputModel(
        type="TODO: SetType",
        description="<to-be-set>",
        config=config_dict
    )


def generate_compute_block() -> ComputeBlock:
    """
    Converts the Settings to a ComputeBlock
    """
    entrypoints = {}
    for entrypoint, func in _registered_functions.items():
        envs = {}
        inputs = {}
        outputs = {}

        if func["settings"]:
            entrypoint_settings_class = func["settings"]
            for key, value in entrypoint_settings_class.model_fields.items():
                if (
                    isinstance(value.default_factory, type) and
                    issubclass(value.default_factory, InputSettings)
                ):
                    inputs[key] = _build_input_output_dict_from_class(
                        value.default_factory
                    )
                elif (
                    isinstance(value.default_factory, type) and
                    issubclass(value.default_factory, OutputSettings)
                ):
                    outputs[key] = _build_input_output_dict_from_class(
                        value.default_factory
                    )
                else:
                    envs[key] = _get_pydantic_default_value_or_none(value)

        entrypoints[entrypoint] = Entrypoint(
            description="<tbd>",
            envs=envs,
            inputs=inputs,
            outputs=outputs
        )

    return ComputeBlock(
        name="<tbs>",
        description="<tbs>",
        author="<tbs>",
        entrypoints=entrypoints,
        docker_image="<tbs>"
    )
