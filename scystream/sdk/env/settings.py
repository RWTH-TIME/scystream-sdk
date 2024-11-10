from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Type

ENV_FILE_ENCODING = "utf-8"


class BaseENVSettings(BaseSettings):
    """
    This class acts as the BaseClass which can be used to define custom
    ENV-Variables which can be used across the ComputeBlock & for entrypoints
    This definition, and pydantic, will then take care of validating the envs
    """

    model_config = SettingsConfigDict(
        env_file_encoding=ENV_FILE_ENCODING,
        case_sensitive=True,
        extra="ignore"
    )

    @classmethod
    def load_settings(
        cls: Type["BaseENVSettings"],
        env_file: str = ".env"
    ) -> "BaseENVSettings":
        """
        load_settings loads the env file. The name of the env_file can be
        passed as an argument.
        Returns the parsed ENVs
        """
        return cls(_env_file=env_file, _env_file_encoding=ENV_FILE_ENCODING)
