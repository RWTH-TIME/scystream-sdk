import functools

from typing import Callable, Type, Optional
from .env.settings import BaseENVSettings
from pydantic import ValidationError

_registered_functions = {}


def entrypoint(settings_class: Optional[Type[BaseENVSettings]] = None):
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
                    settings = settings_class.from_env()
                except ValidationError as e:
                    raise ValueError(f"Invalid environment configuration: {e}")

                return func(settings, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        _registered_functions[func.__name__] = wrapper
        return wrapper
    return decorator


def get_registered_functions():
    """Returns a dictionary of registered entrypoint functions."""
    return _registered_functions
