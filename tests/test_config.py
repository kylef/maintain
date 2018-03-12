import unittest

from maintain.config import Configuration

from tests.utils import temp_directory, touch


class ConfigurationTests(unittest.TestCase):
    def test_loading_no_file(self):
        with temp_directory():
            configuration = Configuration.load()
            self.assertEqual(configuration.release, {})

    def test_loading_file_maintain_yml(self):
        with temp_directory():
            touch('.maintain.yml', 'release:\n  test: value')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), 'value')

    def test_loading_file_maintain_yaml(self):
        with temp_directory():
            touch('.maintain.yaml', 'release:\n  test: value')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), 'value')

    def test_loading_file_config_maintain_yml(self):
        with temp_directory():
            touch('.maintain/config.yml', 'release:\n  test: value')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), 'value')

    def test_loading_file_config_maintain_yaml(self):
        with temp_directory():
            touch('.maintain/config.yaml', 'release:\n  test: value')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), 'value')

    def test_loading_multiple_file(self):
        with temp_directory():
            touch('.maintain.yaml')
            touch('.maintain.yml')

            with self.assertRaises(Exception):
                Configuration.load()
