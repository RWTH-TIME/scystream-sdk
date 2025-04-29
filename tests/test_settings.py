import yaml
from pathlib import Path
from scystream.sdk.config.entrypoints import TEST_reset_registered_functions
import unittest
import os
from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import EnvSettings, InputSettings, \
    OutputSettings, PostgresSettings, FileSettings
from scystream.sdk.config.config_loader import \
    validate_config_with_code, get_compute_block, \
    generate_config_from_compute_block
from scystream.sdk.config import SDKConfig

# Validate Cfgs


class SimpleSettingsInputOne(InputSettings):
    TEST: str = "test"


class SimpleSettingsOutputOne(OutputSettings):
    OUT: str = "out"


class PgTestOutputOne(PostgresSettings, OutputSettings):
    __identifier__ = "my_pg"
    EXTENDS: str = "test"
    pass


class FileTestInputOne(FileSettings, InputSettings):
    __identifier__ = "my_file_one"
    pass


class SettingOtherTypes(EnvSettings):
    LANGUAGE: str = "de"
    input_one: FileTestInputOne
    output: PgTestOutputOne


class SimpleSettings(EnvSettings):
    LANGUAGE: str = "de"

    input_one: SimpleSettingsInputOne
    output_one: SimpleSettingsOutputOne

# WithoutDefaults


class WithoutDefaultsInputOne(InputSettings):
    TEST: str


class WithoutDefaults(EnvSettings):
    LANGUAGE: str  # MUST BE SET

    input_one: WithoutDefaultsInputOne


class TestSettings(unittest.TestCase):
    TEST_SETTINGS_FILES = "tests/test_setting_files/"
    global_config = SDKConfig()

    def tearDown(self):
        TEST_reset_registered_functions()

    def test_generate_config_from_code(self):
        generated_config_path = Path(f"{self.TEST_SETTINGS_FILES}/gen.yaml")
        reference_config_path = Path(f"{self.TEST_SETTINGS_FILES}/ref.yaml")

        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print("Running...")

        try:
            cb = get_compute_block()
            generate_config_from_compute_block(
                cb, generated_config_path)
        except Exception as e:
            self.fail(f"Exception raised unexpectedly: {e}")

        with generated_config_path.open("r") as gen_file:
            generated_yaml = yaml.safe_load(gen_file)

        with reference_config_path.open("r") as ref_file:
            reference_yaml = yaml.safe_load(ref_file)

        # Compare the contents
        self.assertEqual(
            generated_yaml, reference_yaml,
            "Generated YAML does not match the reference YAML"
        )

        generated_config_path.unlink()

    def test_generate_config_file_db_type(self):
        generated_config_path = Path(
            f"{self.TEST_SETTINGS_FILES}/gen_more_types.yaml")
        reference_config_path = Path(
            f"{self.TEST_SETTINGS_FILES}/ref_more_types.yaml")

        @entrypoint(SettingOtherTypes)
        def example_entrypoint(settings):
            print("Running...")

        try:
            cb = get_compute_block()
            generate_config_from_compute_block(
                cb, generated_config_path)
        except Exception as e:
            self.fail(f"Exception raised unexpectedly: {e}")

        with generated_config_path.open("r") as gen_file:
            generated_yaml = yaml.safe_load(gen_file)

        with reference_config_path.open("r") as ref_file:
            reference_yaml = yaml.safe_load(ref_file)

        # Compare the contents
        self.assertEqual(
            generated_yaml, reference_yaml,
            "Generated YAML does not match the reference YAML"
        )

        generated_config_path.unlink()

    def test_entrypoint_with_identifier_and_env_override(self):
        """Test if environment variables override settings correctly with
        identifiers."""

        # Set up the environment variables
        env_vars = {
            "my_file_one_S3_HOST": "overridden_host",
            "my_file_one_S3_PORT": "overridden_port",
            "my_file_one_S3_ACCESS_KEY": "overridden_access",
            "my_file_one_S3_SECRET_KEY": "overridden_secret",
            "my_file_one_BUCKET_NAME": "overridden_bucket",
            "my_file_one_FILE_PATH": "overridden_file_path",
            "my_file_one_FILE_NAME": "overridden_file_name",
            "my_pg_PG_USER": "overridden_user",
            "my_pg_PG_PASS": "overridden_pass",
            "my_pg_PG_HOST": "overridden_host",
            "my_pg_PG_PORT": "overridden_port",
            "my_pg_DB_TABLE": "overridden_table"
        }

        # Set the environment variables
        for key, value in env_vars.items():
            os.environ[key] = value

        try:
            @entrypoint(SettingOtherTypes)
            def example_entrypoint(settings):
                return (
                    settings.input_one.S3_HOST,
                    settings.input_one.S3_PORT,
                    settings.input_one.S3_ACCESS_KEY,
                    settings.input_one.S3_SECRET_KEY,
                    settings.input_one.BUCKET_NAME,
                    settings.input_one.FILE_PATH,
                    settings.input_one.FILE_NAME,
                    settings.output.PG_USER,
                    settings.output.PG_PASS,
                    settings.output.PG_HOST,
                    settings.output.PG_PORT,
                    settings.output.DB_TABLE,
                )

            result = example_entrypoint()

            # Expected values
            expected_values = [
                "overridden_host", "overridden_port", "overridden_access",
                "overridden_secret", "overridden_bucket",
                "overridden_file_path", "overridden_file_name",
                "overridden_user", "overridden_pass", "overridden_host",
                "overridden_port", "overridden_table"
            ]

            # Assert that the results match expected values
            for idx, expected in enumerate(expected_values):
                self.assertEqual(result[idx], expected)
        finally:
            # Clean up the environment variables
            for key in env_vars:
                if key in os.environ:
                    del os.environ[key]

    def test_entrypoint_yaml_cfg_different_to_code_cfg(self):
        """
        Tests if the passed settings to entrypoint config is different
        to the one in yaml
        """

        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print("Running example_entrypoint...")

        with self.assertRaises(ValueError):
            validate_config_with_code(
                "example_entrypoint",
                f"{self.TEST_SETTINGS_FILES}/simple_cfg_entrypoint_inv.yaml"
            )

    def test_entrypoint_yaml_cfg_not_different_to_code_cfg(self):
        """
        Tests if the passed settings to the entrypoint config is diffrent
        to the one in yaml
        """

        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print("Running example_entrypoint...")

        try:
            validate_config_with_code(
                "example_entrypoint",
                f"{self.TEST_SETTINGS_FILES}/simple_cfg_entrypoint_v.yaml"
            )
        except Exception:
            self.fail("")

    def test_validate_cfgs_no_error(self):
        """
        Tests if validate_config_with_code works if config and settings
        correspond.
        """
        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print(f"{settings}....")

        try:
            validate_config_with_code(
                config_path=f"{self.TEST_SETTINGS_FILES}/simple_cfg.yaml"
            )
        except Exception:
            self.fail(
                "validate_config_with_code raised an Exception unexpectedly!")

    def test_validate_cfgs_error(self):
        """
        Tests if validate_config_with_code works if config and settings
        do not correspond.
        """
        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print(f"{settings}....")

        invalid_config = f"{self.TEST_SETTINGS_FILES}/simple_cfg_invalid.yaml"
        with self.assertRaises(ValueError):
            validate_config_with_code(
                config_path=invalid_config
            )

    def test_entrypoint_with_setting_default(self):
        """
        Tests if defaults and overriding defaults with ENVs works.
        We use SimpleSettings as they all have a default.
        """

        @entrypoint(SimpleSettings)
        def with_default_settings(settings):
            return settings.input_one.TEST

        result = with_default_settings()
        self.assertEqual(result, "test")

        # set environ
        os.environ["TEST"] = "overridden setting"
        result = with_default_settings()
        # check if overriding works
        self.assertEqual(result, "overridden setting")

        del os.environ["TEST"]

    def test_entrypoint_no_setting_default_one(self):
        # Tests if fails, if ENVs that MUST be set, are not set
        @entrypoint(WithoutDefaults)
        def without_def_settings(settings):
            print("test...")

        # do we fail if environments not set
        with self.assertRaises(ValueError):
            without_def_settings()

    def test_entrypoint_no_setting_default_two(self):
        # Tests if it works, if ENVs that MUST be set, are actually set
        @entrypoint(WithoutDefaults)
        def without_def_settings(settings):
            return (
                settings.LANGUAGE,
                settings.input_one.TEST
            )

        # set environments
        os.environ["LANGUAGE"] = "dummy global"
        os.environ["TEST"] = "dummy input"

        # check if environments have been set
        result = without_def_settings()
        self.assertEqual(result[0], "dummy global")
        self.assertEqual(result[1], "dummy input")

        del os.environ["LANGUAGE"]
        del os.environ["TEST"]


if __name__ == "__main__":
    unittest.main()
