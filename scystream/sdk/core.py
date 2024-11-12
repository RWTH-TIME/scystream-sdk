import functools
from typing import Callable, Type, Optional
from pydantic import ValidationError
from scystream.sdk.config.entrypoints import register_entrypoint
from scystream.sdk.env.settings import EnvSettings


def entrypoint(settings_class: Optional[Type[EnvSettings]] = None):
    """
    Decorator to mark a function as an entrypoint.
    It also loads and injects the settings of the entrypoint.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if settings_class is not None:
                # Load the settings
                try:
                    # load the settings
                    settings = settings_class.get_settings()
                except ValidationError as e:
                    raise ValueError(f"Invalid environment configuration: {e}")

                # inject the settings
                return func(settings, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        register_entrypoint(func.__name__, wrapper, settings_class)
        return wrapper
    return decorator
