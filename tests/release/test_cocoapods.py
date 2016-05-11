import unittest
import os
import shutil
import filecmp

from semantic_version import Version

from maintain.release.cocoapods import CocoaPodsReleaser
from ..utils import temp_directory, touch


class CocoaPodsReleaserTestCase(unittest.TestCase):
    # Detection

    def test_detects_ruby_podspec(self):
        with temp_directory():
            touch('JSONWebToken.podspec')
            self.assertTrue(CocoaPodsReleaser.detect())

    def test_detects_json_podspec(self):
        with temp_directory():
            touch('URITemplate.podspec.json')
            self.assertTrue(CocoaPodsReleaser.detect())

    # Check current version

    def test_detect_current_version_ruby_podspec(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        podspec = os.path.join(fixture_path, 'JSONWebToken.podspec')

        with temp_directory():
            shutil.copyfile(podspec, 'JSONWebToken.podspec')
            version = CocoaPodsReleaser().determine_current_version()
            self.assertEqual(version, Version('1.4.1'))

    def test_detect_current_version_json_podspec(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        podspec = os.path.join(fixture_path, 'URITemplate.podspec.json')

        with temp_directory():
            shutil.copyfile(podspec, 'URITemplate.podspec.json')
            version = CocoaPodsReleaser().determine_current_version()
            self.assertEqual(version, Version('1.2.0'))

    # Verify

    def test_passes_validation_with_json_spec(self):
        with temp_directory():
            touch('URITemplate.podspec.json')
            CocoaPodsReleaser()

    def test_passes_validation_with_ruby_spec(self):
        with temp_directory():
            touch('JSONWebToken.podspec')
            CocoaPodsReleaser()

    def test_fails_validation_with_multiple_podspecs(self):
        with temp_directory():
            touch('URITemplate2.podspec.json')
            touch('URITemplate.podspec.json')

            with self.assertRaises(Exception):
                CocoaPodsReleaser()

    # Bump

    def test_bumps_json_podspec(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        podspec = os.path.join(fixture_path, 'URITemplate.podspec.json')
        bumped_podspec = os.path.join(fixture_path, 'BumpedURITemplate.podspec.json')

        with temp_directory():
            shutil.copyfile(podspec, 'URITemplate.podspec.json')
            CocoaPodsReleaser().bump('1.2.1')
            self.assertTrue(filecmp.cmp('URITemplate.podspec.json', bumped_podspec))

    def test_bumps_ruby_podspec(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        podspec = os.path.join(fixture_path, 'JSONWebToken.podspec')
        bumped_podspec = os.path.join(fixture_path, 'BumpedJSONWebToken.podspec')

        with temp_directory():
            shutil.copyfile(podspec, 'JSONWebToken.podspec')
            CocoaPodsReleaser().bump('2.0.0')
            self.assertTrue(filecmp.cmp('JSONWebToken.podspec', bumped_podspec))
