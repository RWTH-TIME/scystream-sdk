_registered_functions = {}


def register_entrypoint(func_name, func, settings_class):
    _registered_functions[func_name] = {
        "function": func,
        "settings": settings_class
    }


def get_registered_functions():
    return _registered_functions
