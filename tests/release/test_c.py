
import unittest
import os
import shutil
import filecmp

from semantic_version import Version

from maintain.release.c import CReleaser
from ..utils import temp_directory, touch


class CReleaserTestCase(unittest.TestCase):
    # Detection

    def test_detects_version_header_include(self):
        with temp_directory():
            touch('include/znc/version.h')
            self.assertTrue(CReleaser().detect())

    def test_detects_version_header_src(self):
        with temp_directory():
            touch('src/Version.h')
            self.assertTrue(CReleaser().detect())

    # Verify

    def test_passes_validation_with_single_header(self):
        with temp_directory():
            touch('src/version.h')
            CReleaser()

    def test_fails_validation_with_multiple_version_headers(self):
        with temp_directory():
            touch('include/znc/Version.h')
            touch('include/foo/Version.h')
            touch('src/version.h')

            with self.assertRaises(Exception):
                CReleaser()

    # Determine current version

    def test_detect_current_simple_version(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        header = os.path.join(fixture_path, 'SimpleVersion.h')

        with temp_directory():
            os.mkdir('src')
            shutil.copyfile(header, 'src/version.h')
            version = CReleaser().determine_current_version()
            self.assertEqual(version, Version('1.2.0'))

    def test_detect_current_simple_named_version(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        header = os.path.join(fixture_path, 'SimpleNamedVersion.h')

        with temp_directory():
            os.mkdir('src')
            shutil.copyfile(header, 'src/version.h')
            version = CReleaser().determine_current_version()
            self.assertEqual(version, Version('1.2.0'))

    # Bumping

    def test_bumps_version(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        header = os.path.join(fixture_path, 'SimpleVersion.h')
        bumped_header = os.path.join(fixture_path, 'BumpedSimpleVersion.h')

        with temp_directory():
            os.mkdir('src')
            shutil.copyfile(header, 'src/version.h')
            CReleaser().bump('2.5.3')
            self.assertTrue(filecmp.cmp('src/version.h', bumped_header))

    def test_bumping_prelease_unsupported(self):
        with temp_directory():
            touch('src/version.h')
            releaser = CReleaser()

            with self.assertRaises(Exception):
                releaser.bump('2.5.3-beta.0')
