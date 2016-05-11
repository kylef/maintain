import unittest
import os
import shutil
import filecmp

from semantic_version import Version

from maintain.release.python import PythonReleaser
from ..utils import temp_directory, touch


class PythonReleaserTestCase(unittest.TestCase):
    # Determine current version

    def test_detect_current_version(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        package = os.path.join(fixture_path, 'setup.py')

        with temp_directory():
            shutil.copyfile(package, 'setup.py')
            version = PythonReleaser().determine_current_version()
            self.assertEqual(version, Version('0.1.0'))

    # Detection

    def test_detects_package_json(self):
        with temp_directory():
            touch('setup.py')
            self.assertTrue(PythonReleaser.detect())

    # Bumping

    def test_bumps_package_json(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        package = os.path.join(fixture_path, 'setup.py')
        bumped_package = os.path.join(fixture_path, 'bumped-setup.py')

        with temp_directory():
            shutil.copyfile(package, 'setup.py')
            PythonReleaser().bump('1.0.0')
            self.assertTrue(filecmp.cmp('setup.py', bumped_package))
