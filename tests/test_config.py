import unittest
from scystream.sdk.config.config_loader import load_config, ComputeBlock


class TestComputeBlockValidation(unittest.TestCase):
    TEST_CONFIG_FOLDER = "tests/test_config_files"

    def test_valid_config(self):
        try:
            compute_block = load_config(
                "valid_config.yaml", config_path=self.TEST_CONFIG_FOLDER)
            self.assertIsInstance(compute_block, ComputeBlock)
        except Exception:
            self.fail("ComputeBlock raised an Exception unexpectedly!")

    def test_missing_entrypoints(self):
        with self.assertRaises(ValueError):
            load_config("missing_entrypoints.yaml",
                        config_path=self.TEST_CONFIG_FOLDER)

    def test_missing_table_name_for_spark_table(self):
        with self.assertRaises(ValueError):
            load_config("missing_table_name.yaml",
                        config_path=self.TEST_CONFIG_FOLDER)

    def test_invalid_datatypes(self):
        with self.assertRaises(ValueError):
            load_config("invalid_datatype.yaml",
                        config_path=self.TEST_CONFIG_FOLDER)

    def test_not_a_yaml(self):
        with self.assertRaises(ValueError):
            load_config("not_a_yaml.json",
                        config_path=self.TEST_CONFIG_FOLDER)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_config("test.yaml")


if __name__ == "__main__":
    unittest.main()
