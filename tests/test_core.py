import unittest
from scystream_sdk.core import entrypoint, get_registered_functions

class TestEntrypoint(unittest.TestCase):
    def test_entrypoint_registration(self):
        @entrypoint
        def dummy_function():
            return "Hello"

        registered = get_registered_functions()
        self.assertIn("dummy_function", registered)
        self.assertEqual(registered["dummy_function"](), "Hello")

if __name__ == "__main__":
    unittest.main()
