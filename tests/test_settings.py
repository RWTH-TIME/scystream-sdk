import yaml
from pathlib import Path
from scystream.sdk.config.entrypoints import TEST_reset_registered_functions
import unittest
import os
from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import EnvSettings, InputSettings, \
    OutputSettings
from scystream.sdk.scheduler import Scheduler
from scystream.sdk.config.config_loader import \
    validate_config_with_code, get_compute_block, \
    generate_config_from_compute_block
from scystream.sdk.config import SDKConfig

# Validate Cfgs


class SimpleSettingsInputOne(InputSettings):
    TEST: str = "test"


class SimpleSettingsOutputOne(OutputSettings):
    OUT: str = "out"


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

    def test_entrypoint_yaml_cfg_different_to_code_cfg(self):
        # Tests if the passed settings to entrypoint config is different
        # to the one in yaml
        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print("Running example_entrypoint...")

        self.global_config.set_config_path(
            f"{self.TEST_SETTINGS_FILES}/simple_cfg_entrypoint_inv.yaml"
        )

        with self.assertRaises(ValueError):
            Scheduler.execute_function("example_entrypoint")

    def test_entrypoint_yaml_cfg_not_different_to_code_cfg(self):
        # Tests if the passed settings to entrypoint config is different
        # to the one in yaml
        # HINT: TOTAL CONFIG does not fit, only the entrypoint ones fits
        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print("Running example_entrypoint...")

        self.global_config.set_config_path(
            f"{self.TEST_SETTINGS_FILES}/simple_cfg_entrypoint_v.yaml"
        )

        try:
            Scheduler.execute_function("example_entrypoint")
        except Exception:
            self.fail("")

    def test_validate_cfgs_no_error(self):
        # Tests if validate_config_with_code works if config and settings
        # correspond
        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print(f"{settings}....")

        self.global_config.set_config_path(
            f"{self.TEST_SETTINGS_FILES}/simple_cfg.yaml")

        try:
            validate_config_with_code()
        except Exception:
            self.fail(
                "validate_config_with_code raised an Exception unexpectedly!")

    def test_validate_cfgs_error(self):
        # Tests if validate_config_with_code works if config and settings
        # do not correspond
        @entrypoint(SimpleSettings)
        def example_entrypoint(settings):
            print(f"{settings}....")

        self.global_config.set_config_path(
            f"{self.TEST_SETTINGS_FILES}/simple_cfg_invalid.yaml")

        with self.assertRaises(ValueError):
            validate_config_with_code()

    def test_entrypoint_with_setting_default(self):
        # Tests if defaults and overriding defaults with ENvs works
        # We use SimpleSettings as they all have a default
        @entrypoint(SimpleSettings)
        def with_default_settings(settings):
            return settings.input_one.TEST

        self.global_config.set_config_path(
            f"{self.TEST_SETTINGS_FILES}/simple_cfg.yaml")

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

        self.global_config.set_config_path(
            f"{self.TEST_SETTINGS_FILES}/without_default_settings.yaml")

        # do we fail if environments not set
        with self.assertRaises(ValueError):
            Scheduler.execute_function("without_def_settings")

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
