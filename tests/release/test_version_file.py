import unittest

from semantic_version import Version

from maintain.release.version_file import VersionFileReleaser
from ..utils import temp_directory, touch


class VersionFileReleaserTestCase(unittest.TestCase):
    # Determine current version

    def test_detect_current_version(self):
        with temp_directory():
            with open('VERSION', 'w') as fp:
                fp.write('1.0.0\n')

            version = VersionFileReleaser().determine_current_version()
            self.assertEqual(version, Version('1.0.0'))

    # Detection

    def test_detects_version_file(self):
        with temp_directory():
            touch('VERSION')
            self.assertTrue(VersionFileReleaser().detect())

    # Bumping

    def test_bumps_package_json(self):
        with temp_directory():
            with open('VERSION', 'w') as fp:
                fp.write('1.0.0\n')

            VersionFileReleaser().bump('2.0.0')

            with open('VERSION') as fp:
                self.assertEqual(fp.read(), '2.0.0\n')
