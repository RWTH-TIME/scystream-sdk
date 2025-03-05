from typing import Union
from pydantic_core import PydanticUndefinedType
from scystream.sdk.config.models import ComputeBlock, Entrypoint, \
    InputOutputModel, FILE_TYPE_IDENTIFIER, PG_TABLE_TYPE_IDENTIFIER, \
    CUSTOM_TYPE_IDENTIFIER
from scystream.sdk.env.settings import InputSettings, \
    OutputSettings, FileSettings, PostgresSettings
from scystream.sdk.config.entrypoints import get_registered_functions


def _get_pydantic_default_value_or_none(value):
    if type(value.default) is PydanticUndefinedType:
        return None
    return value.default


def _get_io_type(subj: Union[InputSettings, OutputSettings]) -> str:
    """
    Determines the type of input/output based on the subject class.

    :param subject: The settings class
    :return: The determined type ("file", "pg_table", "custom")
    """

    if issubclass(subj, FileSettings):
        return FILE_TYPE_IDENTIFIER
    elif issubclass(subj, PostgresSettings):
        return PG_TABLE_TYPE_IDENTIFIER
    return CUSTOM_TYPE_IDENTIFIER


def _build_input_output_dict_from_class(
    subject: Union[InputSettings, OutputSettings]
):
    config_dict = {}
    identifier = getattr(subject, "__identifier__", None)
    for key, value in subject.model_fields.items():
        default_value = _get_pydantic_default_value_or_none(value)

        if identifier:
            key = f"{identifier}_{key}"

        config_dict[key] = default_value

    return InputOutputModel(
        type=_get_io_type(subject),
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
