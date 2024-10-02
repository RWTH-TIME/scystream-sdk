from .core import get_registered_functions

class Scheduler:
    @staticmethod
    def list_entrypoints():
        """List all registered entrypoint functions."""
        functions = get_registered_functions()
        for name in functions:
            print(f"'{name}' is available as an entrypoint.")
            
    @staticmethod
    def execute_function(name, *args, **kwargs):
        functions = get_registered_functions()
        if name in functions:
            return functions[name](*args, **kwargs)
        else:
            raise Exception(f"No entrypoint found with the name: {name}")

