import unittest
import os
import shutil
import filecmp

from semantic_version import Version

from maintain.release.gem import GemReleaser
from ..utils import temp_directory, touch


class PythonReleaserTestCase(unittest.TestCase):
    # Determine current version

    def test_detect_current_version(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        package = os.path.join(fixture_path, 'cocoapods_deintegrate.gemspec')

        with temp_directory():
            shutil.copyfile(package, 'cocoapods_deintegrate.gemspec')
            version = GemReleaser().determine_current_version()
            self.assertEqual(version, Version('1.0.0'))

    # Detection

    def test_detects_gemspec(self):
        with temp_directory():
            touch('cocoapods_deintegrate.gemspec')
            self.assertTrue(GemReleaser.detect())

    # Bumping

    def test_bumps_package_json(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        package = os.path.join(fixture_path, 'cocoapods_deintegrate.gemspec')
        bumped_package = os.path.join(fixture_path, 'bumped-cocoapods_deintegrate.gemspec')

        with temp_directory():
            shutil.copyfile(package, 'cocoapods_deintegrate.gemspec')
            GemReleaser().bump('1.1.0')
            self.assertTrue(filecmp.cmp('cocoapods_deintegrate.gemspec', bumped_package))
