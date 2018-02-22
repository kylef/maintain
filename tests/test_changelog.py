import os
import unittest
import shutil

from maintain.changelog import parse_changelog


class ChangelogTestCase(unittest.TestCase):
    def test_parse_changelog(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'release', 'fixtures')
        changelog_path = os.path.join(fixture_path, 'CHANGELOG.md')

        changelog = parse_changelog(changelog_path)

        self.assertEqual(changelog.name, 'swiftenv Changelog')
        self.assertEqual(len(changelog.releases), 2)
        self.assertEqual(changelog.releases[0].name, 'Master')
        self.assertEqual(changelog.releases[1].name, '1.0.0')

