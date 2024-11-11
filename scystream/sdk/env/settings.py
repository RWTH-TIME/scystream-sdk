from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union, List, get_type_hints
from pydantic import Field

ENV_FILE_ENCODING = "utf-8"


class BaseENVSettings(BaseSettings):
    """
    Allow kwargs to propagate to any fields whose default factory extends
    BaseSettings,

    This is mostly to allow _env_file to be passed through.
    """
    model_config = SettingsConfigDict(
        env_file_encoding=ENV_FILE_ENCODING,
        case_sensitive=True,
        extra="ignore"
    )

    @classmethod
    def from_env(
        cls,
        env_file: Union[str, Path, List[Union[str, Path]]] = None,
        *args,
        **kwargs
    ):
        return cls(propagate_kwargs={"_env_file": env_file}, *args, **kwargs)

    @classmethod
    def _basesettings_fields(cls):
        """
        :return a dict of field_name: default_factory for any fields that
        extend BaseSettings
        """
        type_hints = get_type_hints(cls)
        return {
            name: typ for name, typ in type_hints.items()
            if isinstance(typ, type) and issubclass(typ, BaseSettings)

        }

    @classmethod
    def _propagate_kwargs(cls, kwargs):
        """
        Any settings that extend BaseSettings be passed the kwargs.
        """
        sub_settings = cls._basesettings_fields()
        for name, field_type in sub_settings.items():
            kwargs[name] = field_type(**kwargs)
        return kwargs

    def __init_subclass__(cls, **kwargs):
        """
        Automatically set up nested settings fields with default_factory.
        """
        super().__init_subclass__(**kwargs)
        type_hints = get_type_hints(cls)
        for field_name, field_type in type_hints.items():
            if isinstance(field_type, type) and issubclass(
                    field_type, BaseSettings):
                # Set a default factory for nested BaseSettings fields
                default_field = Field(default_factory=field_type)
                setattr(cls, field_name, default_field)

    def __init__(self, propagate_kwargs=None, *args, **kwargs):
        if propagate_kwargs:
            kwargs = self._propagate_kwargs(propagate_kwargs)
        super().__init__(*args, **kwargs)
