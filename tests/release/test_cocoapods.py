import unittest
import os
import shutil
import filecmp

from semantic_version import Version

from maintain.release.cocoapods import CocoaPodsReleaser
from ..utils import temp_directory, touch


class CocoaPodsReleaserTestCase(unittest.TestCase):
    # Detection

    def test_detects_podspec(self):
        with temp_directory() as directory:
            touch('URITemplate.podspec')
            self.assertTrue(CocoaPodsReleaser.detect())

    def test_detects_json_podspec(self):
        with temp_directory() as directory:
            touch('URITemplate.podspec.json')
            self.assertTrue(CocoaPodsReleaser.detect())

    # Check current version

    def test_detect_current_version(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        podspec = os.path.join(fixture_path, 'URITemplate.podspec.json')
        bumped_podspec = os.path.join(fixture_path, 'BumpedURITemplate.podspec.json')

        with temp_directory() as directory:
            shutil.copyfile(podspec, 'URITemplate.podspec.json')
            version = CocoaPodsReleaser().determine_current_version()
            self.assertEqual(version, Version('1.2.0'))

    # Verify

    def test_passes_validation(self):
        with temp_directory() as directory:
            touch('URITemplate.podspec.json')
            CocoaPodsReleaser()

    def test_fails_validation_with_ruby_podspecs(self):
        # TODO: Ruby podspecs should be somehow supported in the future

        with temp_directory() as directory:
            touch('URITemplate.podspec')

            with self.assertRaises(Exception):
                CocoaPodsReleaser()

    def test_fails_validation_with_multiple_podspecs(self):
        with temp_directory() as directory:
            touch('URITemplate2.podspec.json')
            touch('URITemplate.podspec.json')

            with self.assertRaises(Exception):
                CocoaPodsReleaser()

    # Bump

    def test_bumps_json_podspec(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        podspec = os.path.join(fixture_path, 'URITemplate.podspec.json')
        bumped_podspec = os.path.join(fixture_path, 'BumpedURITemplate.podspec.json')

        with temp_directory() as directory:
            shutil.copyfile(podspec, 'URITemplate.podspec.json')
            CocoaPodsReleaser().bump('1.2.1')
            self.assertTrue(filecmp.cmp('URITemplate.podspec.json', bumped_podspec))
