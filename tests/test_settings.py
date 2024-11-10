import unittest
import os
from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import BaseENVSettings


class WithDefaultSettings(BaseENVSettings):
    DUMMY_SETTING: str = "this is a dummy setting"


class NoDefaultSetting(BaseENVSettings):
    DUMMY_SETTING: str


class TestSettings(unittest.TestCase):
    def test_entrypoint_with_setting_default(self):
        @entrypoint(WithDefaultSettings)
        def with_default_settings(settings):
            return settings.DUMMY_SETTING

        result = with_default_settings()
        self.assertEqual(result, "this is a dummy setting")

        """
        environment is set
        """
        os.environ["DUMMY_SETTING"] = "overridden setting"
        result = with_default_settings()
        self.assertEqual(result, "overridden setting")
        del os.environ["DUMMY_SETTING"]

    def test_entrypoint_with_no_setting_default(self):
        @entrypoint(NoDefaultSetting)
        def with_no_default_settings(settings):
            return settings.DUMMY_SETTING

        with self.assertRaises(ValueError):
            with_no_default_settings()

        """
        environemnt is set
        """
        os.environ["DUMMY_SETTING"] = "required setting"
        result = with_no_default_settings()
        self.assertEqual(result, "required setting")
        del os.environ["DUMMY_SETTING"]


if __name__ == "__main__":
    unittest.main()
