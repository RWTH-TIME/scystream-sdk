import unittest
import os
from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import EnvSettings
from scystream.sdk.scheduler import Scheduler


class DummyInputSettings(EnvSettings):
    DUMMY_INPUT: str = "test"


class WithDefaultSettings(EnvSettings):
    DUMMY_GLOBAL: str = "dummy global var"

    dummy_input_settings: DummyInputSettings


class DummyInputSettingsNoDef(EnvSettings):
    DUMMY_INPUT: str


class WithoutDefaultSettings(EnvSettings):
    DUMMY_GLOBAL: str

    dummy_input_settings_no_def: DummyInputSettingsNoDef


class WithoutDefaultNoNesting(EnvSettings):
    TEST: str = "teststr"
    MUST_SET: str


class SubOne(EnvSettings):
    ONE: str
    TWO: str


class SubTwo(EnvSettings):
    TEST: str
    NO_DEF: str


class TwoSubclasses(EnvSettings):
    GLOBAL: str

    input_one: SubOne
    input_two: SubTwo


class TestSettings(unittest.TestCase):
    def test_entrypoint_with_setting_default(self):
        @entrypoint(WithDefaultSettings)
        def with_default_settings(settings):
            return settings.dummy_input_settings.DUMMY_INPUT

        result = with_default_settings()
        self.assertEqual(result, "test")

        # set environ
        os.environ["DUMMY_INPUT"] = "overridden setting"
        result = with_default_settings()
        # check if overriding works
        self.assertEqual(result, "overridden setting")

        del os.environ["DUMMY_INPUT"]

    def test_entrypoint_no_setting_default_one(self):
        @entrypoint(WithoutDefaultSettings)
        def without_def_settings(settings):
            print("test...")

        # do we fail if environments not set
        with self.assertRaises(ValueError):
            Scheduler.execute_function("without_def_settings")

    def test_entrypoint_no_setting_default_two(self):
        @entrypoint(WithoutDefaultSettings)
        def without_def_settings(settings):
            return (
                settings.DUMMY_GLOBAL,
                settings.dummy_input_settings_no_def.DUMMY_INPUT
            )

        # set environments
        os.environ["DUMMY_GLOBAL"] = "dummy global"
        os.environ["DUMMY_INPUT"] = "dummy input"

        # check if environments have been set
        result = without_def_settings()
        self.assertEqual(result[0], "dummy global")
        self.assertEqual(result[1], "dummy input")

        del os.environ["DUMMY_GLOBAL"]
        del os.environ["DUMMY_INPUT"]

    def test_entrypoint_no_setting_defautl_three(self):
        @entrypoint(WithoutDefaultNoNesting)
        def no_nesting(settings):
            print("testing...")

        with self.assertRaises(ValueError):
            Scheduler.execute_function("no_nesting")

    def test_two_subs(self):
        @entrypoint(TwoSubclasses)
        def two_subs(settings):
            return (
                settings.GLOBAL,
                settings.input_one.ONE,
                settings.input_one.TWO,
                settings.input_two.TEST,
                settings.input_two.NO_DEF
            )

        os.environ["GLOBAL"] = "global"
        os.environ["ONE"] = "one"
        os.environ["TWO"] = "two"
        os.environ["TEST"] = "test"
        os.environ["NO_DEF"] = "no_def"

        result = two_subs()
        self.assertEqual(result[0], "global")
        self.assertEqual(result[1], "one")
        self.assertEqual(result[2], "two")
        self.assertEqual(result[3], "test")
        self.assertEqual(result[4], "no_def")

        del os.environ["GLOBAL"]
        del os.environ["ONE"]
        del os.environ["TWO"]
        del os.environ["TEST"]
        del os.environ["NO_DEF"]


if __name__ == "__main__":
    unittest.main()
