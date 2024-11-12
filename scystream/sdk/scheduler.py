from scystream.sdk.config.entrypoints import get_registered_functions
from scystream.sdk.config import validate_config_with_code


class Scheduler:
    @staticmethod
    def list_entrypoints():
        """List all registered entrypoint functions."""
        functions = get_registered_functions()
        for name in functions:
            print(f"'{name}' is available as an entrypoint.")

    @staticmethod
    def execute_function(name, *args, **kwargs):
        """
        Validate the in code defined entrypoints
        with the settings defined in the cfg file
        """
        validate_config_with_code(entrypoint_name=name)

        functions = get_registered_functions()
        if name in functions:
            return functions[name]["function"](*args, **kwargs)
        else:
            raise Exception(f"No entrypoint found with the name: {name}")
