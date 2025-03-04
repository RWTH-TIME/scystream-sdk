from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union, List, get_type_hints
from pydantic import Field

ENV_FILE_ENCODING = "utf-8"


class EnvSettings(BaseSettings):
    """
    A base class for settings that loads and parses configurations
    from environment variables or files and supports nested settings models
    that extend `BaseSettings`.

    This class is designed to allow the propagation of keyword arguments
    to any fields whose type is a subclass of `BaseSettings`, such as
    nested settings models. It is primarily used to handle the `_env_file`
    argument to specify environment files for loading configuration.

    The `model_config` attribute is configured to:

    - Set the encoding of environment files to UTF-8.

    - Make environment variable names case-sensitive.

    - Ignore extra fields that are not defined in the model.
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
        """
        Create an instance of the settings class from environment files
        or other keyword arguments.

        This method allows environment files to be specified and used to
        populate the settings.

        :param env_file: The environment file(s) to load from. Can be a
                          single file path or a list of paths.
        :param args: Additional positional arguments to pass to the
            `BaseSettings` constructor.
        :param kwargs: Additional keyword arguments to pass to the
            `BaseSettings` constructor.
        :return: An instance of the settings class with values populated
                 from the environment files and any additional arguments.
        """
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

    @classmethod
    def get_settings(cls):
        """
        Retrieves the settings instance, loading the configuration from
        the `.env` file.

        :return: An instance of the settings class with values populated
                 from the `.env` file.
        """
        return cls.from_env(env_file=".env")

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


class InputSettings(EnvSettings):
    """
    A subclass of `EnvSettings` that can be extended to define input-related
    settings for a specific use case.
    """


class OutputSettings(EnvSettings):
    """
    A subclass of `EnvSettings` that can be extended to define output-related
    settings for a specific use case.
    """


class FileSettings(EnvSettings):
    """
    A subclass of `EnvSettings` that should be used to define file inputs
    and outputs.
    """
    S3_HOST: str
    S3_PORT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    BUCKET_NAME: str
    FILE_PATH: str
    FILE_NAME: str

    def __init_subclass__(cls, **kwargs):
        """
        Enforce __identifier__ for FileSettings subclasses.
        """
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '__identifier__'):
            raise TypeError(
                f"Class {cls.__name__} must define an __identifier__ attribute"
                "because it inherits from FileSettings"
            )
        # Dynamically set the env_prefix based on __identifier__
        cls.model_config = SettingsConfigDict(
            env_file_encoding=ENV_FILE_ENCODING,
            case_sensitive=True,
            extra="ignore",
            env_prefix=f"{cls.__identifier__}_"
        )


class PostgresSettings(EnvSettings):
    """
    A subclass of `EnvSettings` that should be used to define db_table
    inputs and outputs located on a postgres db.
    """
    PG_USER: str
    PG_PASS: str
    PG_HOST: str
    PG_PORT: str
    DB_TABLE: str

    def __init_subclass__(cls, **kwargs):
        """
        Enforce __identifier__ for PostgresSettings subclasses.
        """
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '__identifier__'):
            raise TypeError(
                f"Class {cls.__name__} must define an __identifier__ attribute"
                "because it inherits from PostgresSettings"
            )
        # Dynamically set the env_prefix based on __identifier__
        cls.model_config = SettingsConfigDict(
            env_file_encoding=ENV_FILE_ENCODING,
            case_sensitive=True,
            extra="ignore",
            env_prefix=f"{cls.__identifier__}_"
        )


class CustomSettings(EnvSettings):
    """
    A subclass of `EnvSettings` that can be extended to define the
    settings for a custom use case.
    """
