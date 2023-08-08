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
            touch('.maintain.yml', 'release:\n  test: {}')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), {})

    def test_loading_file_maintain_yaml(self):
        with temp_directory():
            touch('.maintain.yaml', 'release:\n  test: {}')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), {})

    def test_loading_file_config_maintain_yml(self):
        with temp_directory():
            touch('.maintain/config.yml', 'release:\n  test: {}')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), {})

    def test_loading_file_config_maintain_yaml(self):
        with temp_directory():
            touch('.maintain/config.yaml', 'release:\n  test: {}')

            configuration = Configuration.load()
            self.assertEqual(configuration.release.get('test'), {})

    def test_loading_multiple_file(self):
        with temp_directory():
            touch('.maintain.yaml')
            touch('.maintain.yml')

            with self.assertRaises(Exception):
                Configuration.load()

    def test_loading_file_validation(self):
        with temp_directory():
            touch('.maintain.yml', 'release: []')

            with self.assertRaises(Exception):
                configuration.load()

    # Validation

    def test_validate_release_object(self):
        with self.assertRaises(Exception):
            Configuration.validate({'release': []})

    def test_validate_release_releaser_object(self):
        with self.assertRaises(Exception):
            Configuration.validate({'release': {'test': []}})

    def test_validate_valid_releaser(self):
        Configuration.validate(
            {
                'release': {
                    'git': {
                        'commit_format': 'Hello World',
                        'tag_format': '{version}',
                    }
                }
            }
        )

    def test_validate_invalid_releaser(self):
        with self.assertRaises(Exception):
            Configuration.validate(
                {
                    'release': {
                        'git': {
                            'commit_format': 'Hello World',
                            'tag_format': '{version}',
                            'unknown': 'x',
                        }
                    }
                }
            )
