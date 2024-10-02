import functools

_registered_functions = {}

def entrypoint(func):
    """Decorator to mark a function as an entrypoint."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    _registered_functions[func.__name__] = func
    return wrapper

def get_registered_functions():
    """Returns a dictionary of registered entrypoint functions."""
    return _registered_functions
