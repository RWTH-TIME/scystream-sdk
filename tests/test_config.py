import unittest
from scystream.sdk.config import load_config
from scystream.sdk.config.models import ComputeBlock


class TestComputeBlockValidation(unittest.TestCase):
    TEST_CONFIG_FOLDER = "tests/test_config_files"

    def test_valid_config(self):
        try:
            compute_block = load_config(
                f"{self.TEST_CONFIG_FOLDER}/valid_config.yaml")
            self.assertIsInstance(compute_block, ComputeBlock)
        except Exception:
            self.fail("ComputeBlock raised an Exception unexpectedly!")

    def test_missing_entrypoints(self):
        with self.assertRaises(ValueError):
            load_config(f"{self.TEST_CONFIG_FOLDER}/missing_entrypoints.yaml")

    def test_invalid_datatypes(self):
        with self.assertRaises(ValueError):
            load_config(f"{self.TEST_CONFIG_FOLDER}/invalid_datatype.yaml")

    def test_not_a_yaml(self):
        with self.assertRaises(ValueError):
            load_config(f"{self.TEST_CONFIG_FOLDER}/not_a_yaml.json")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_config(f"{self.TEST_CONFIG_FOLDER}/testyamll")


if __name__ == "__main__":
    unittest.main()
