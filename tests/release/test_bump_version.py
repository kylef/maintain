import unittest

from semantic_version import Version

from maintain.release.version_file import VersionFileReleaser
from ..utils import temp_directory, touch


class BumpVersionTestCase(unittest.TestCase):
    # Detection

    def test_detects_version_file(self):
        with temp_directory():
            touch('VERSION')
            self.assertTrue(VersionFileReleaser.detect())

    def test_doesnt_detect_without_version_file(self):
        with temp_directory():
            self.assertFalse(VersionFileReleaser.detect())

    # Determing current version

    def test_determine_current_version(self):
        releaser = VersionFileReleaser()

        with temp_directory():
            touch('VERSION', '0.2.6')
            version = releaser.determine_current_version()
            self.assertEqual(version, Version('0.2.6'))

    # Bumping

    def test_bumps_version_file(self):
        releaser = VersionFileReleaser()

        with temp_directory():
            touch('VERSION', '2.2.12')
            releaser.bump('2.3.0')

            with open('VERSION') as fp:
                self.assertEqual(fp.read(), '2.3.0\n')
