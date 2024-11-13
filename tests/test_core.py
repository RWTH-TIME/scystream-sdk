import unittest
from scystream.sdk.core import entrypoint
from scystream.sdk.config.entrypoints import get_registered_functions
from scystream.sdk.config.entrypoints import TEST_reset_registered_functions


class TestEntrypoint(unittest.TestCase):
    def tearDown(self):
        TEST_reset_registered_functions()

    def test_entrypoint_registration(self):
        @entrypoint()
        def dummy_function():
            return "Hello"

        registered = get_registered_functions()
        self.assertIn("dummy_function", registered)
        self.assertEqual(registered["dummy_function"]["function"](), "Hello")


if __name__ == "__main__":
    unittest.main()
