from typing import Union
from pydantic_core import PydanticUndefinedType
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel
from scystream.sdk.env.settings import InputSettings, \
    OutputSettings
from scystream.sdk.config.entrypoints import get_registered_functions


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


def get_compute_block() -> ComputeBlock:
    """
    Converts Entrypoints & Settings defined in the Code
    to a ComputeBlock instance.
    """
    entrypoints = {}
    for entrypoint, func in get_registered_functions().items():
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
            envs=envs if envs != {} else None,
            inputs=inputs if inputs != {} else None,
            outputs=outputs if outputs != {} else None
        )

    return ComputeBlock(
        name="<tbs>",
        description="<tbs>",
        author="<tbs>",
        entrypoints=entrypoints,
        docker_image="<tbs>"
    )
