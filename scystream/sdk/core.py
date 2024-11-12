import functools
from typing import Callable, Type, Optional
from scystream.sdk.env.settings import EnvSettings
from pydantic import ValidationError

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
                # TODO: validate the entrypoint settings with the config yaml

                try:
                    # load the settings
                    settings = settings_class.get_settings()
                except ValidationError as e:
                    raise ValueError(f"Invalid environment configuration: {e}")

                # inject the settings
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
    return _registered_functions
