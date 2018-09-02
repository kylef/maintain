import unittest
import mock

from requests.models import Response

from maintain.config import Configuration

from tests.utils import temp_directory, touch


def config_response(url):
    assert(url == 'https://example.com/maintain.yaml')
    response = Response()
    response.status_code = 200
    response._content = b'release:\n  git:\n    tag_format: v{version}'
    return response


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

            with self.assertRaisesRegexp(Exception, "Failed validating 'type'"):
                Configuration.load()

    # Loading Remote Config

    @mock.patch('requests.get', mock.Mock(side_effect=config_response))
    def test_loading_remote_https_file(self):
        with temp_directory():
            touch('.maintain.yaml', '$ref: https://example.com/maintain.yaml')

            config = Configuration.load()

        self.assertEqual(config.release['git'], {'tag_format': 'v{version}'})

    def test_loading_remote_http_file(self):
        with temp_directory():
            touch('.maintain.yaml', '$ref: http://example.com/maintain.yaml')

            with self.assertRaisesRegexp(Exception, 'Remote configuration reference http://example.com/maintain.yaml must be https'):
                Configuration.load()

    def test_loading_remote_local_file(self):
        with temp_directory():
            touch('.maintain.yaml', '$ref: config/maintain.yaml')

            with self.assertRaisesRegexp(Exception, 'Remote configuration reference config/maintain.yaml must be https'):
                Configuration.load()

    # Validation

    def test_validate_release_object(self):
        with self.assertRaises(Exception):
            Configuration.validate({'release': []})

    def test_validate_release_releaser_object(self):
        with self.assertRaises(Exception):
            Configuration.validate({'release': {'test': []}})

    def test_validate_valid_releaser(self):
        Configuration.validate({
            'release': {
                'git': {
                    'commit_format': 'Hello World',
                    'tag_format': '{version}',
                }
            }
        })

    def test_validate_invalid_releaser(self):
        with self.assertRaises(Exception):
            Configuration.validate({
                'release': {
                    'git': {
                        'commit_format': 'Hello World',
                        'tag_format': '{version}',
                        'unknown': 'x',
                    }
                }
            })
