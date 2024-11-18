import unittest
from scystream.sdk.config import load_config, SDKConfig
from scystream.sdk.config.models import ComputeBlock


class TestComputeBlockValidation(unittest.TestCase):
    TEST_CONFIG_FOLDER = "tests/test_config_files"
    global_config = SDKConfig()

    def test_valid_config(self):
        try:
            self.global_config.set_config_path(
                f"{self.TEST_CONFIG_FOLDER}/valid_config.yaml")
            compute_block = load_config()
            self.assertIsInstance(compute_block, ComputeBlock)
        except Exception:
            self.fail("ComputeBlock raised an Exception unexpectedly!")

    def test_missing_entrypoints(self):
        self.global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/missing_entrypoints.yaml")
        with self.assertRaises(ValueError):
            load_config()

    def test_invalid_datatypes(self):
        self.global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/invalid_datatype.yaml")
        with self.assertRaises(ValueError):
            load_config()

    def test_not_a_yaml(self):
        self.global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/not_a_yaml.json")
        with self.assertRaises(ValueError):
            load_config()

    def test_file_not_found(self):
        self.global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/testyamll")
        with self.assertRaises(FileNotFoundError):
            load_config()


if __name__ == "__main__":
    unittest.main()
