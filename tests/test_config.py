import unittest
from scystream.sdk.config.config_loader import load_config, \
    ComputeBlock, global_config


class TestComputeBlockValidation(unittest.TestCase):
    TEST_CONFIG_FOLDER = "tests/test_config_files"

    def test_valid_config(self):
        try:
            global_config.set_config_path(
                f"{self.TEST_CONFIG_FOLDER}/valid_config.yaml")
            compute_block = load_config()
            self.assertIsInstance(compute_block, ComputeBlock)
        except Exception:
            self.fail("ComputeBlock raised an Exception unexpectedly!")

    def test_missing_entrypoints(self):
        global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/missing_entrypoints.yaml")
        with self.assertRaises(ValueError):
            load_config()

    def test_invalid_datatypes(self):
        global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/invalid_datatype.yaml")
        with self.assertRaises(ValueError):
            load_config()

    def test_not_a_yaml(self):
        global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/not_a_yaml.json")
        with self.assertRaises(ValueError):
            load_config()

    def test_file_not_found(self):
        global_config.set_config_path(
            f"{self.TEST_CONFIG_FOLDER}/testyamll")
        with self.assertRaises(FileNotFoundError):
            load_config()


if __name__ == "__main__":
    unittest.main()
