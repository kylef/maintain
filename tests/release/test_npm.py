import unittest
import os
import shutil
import filecmp

from maintain.release.npm import NPMReleaser
from ..utils import temp_directory, touch


class NPMReleaserTestCase(unittest.TestCase):
    # Detection

    def test_detects_package_json(self):
        with temp_directory() as directory:
            touch('package.json')
            self.assertTrue(NPMReleaser.detect())

    # Bumping

    def test_bumps_package_json(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        package = os.path.join(fixture_path, 'package.json')
        bumped_package = os.path.join(fixture_path, 'bumped-package.json')

        with temp_directory() as directory:
            shutil.copyfile(package, 'package.json')
            NPMReleaser().bump('0.3.0')
            self.assertTrue(filecmp.cmp('package.json', bumped_package))
