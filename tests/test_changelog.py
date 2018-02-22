import os
import unittest

from tests.utils import temp_directory, touch

from maintain.changelog import parse_changelog, extract_last_changelog


class ChangelogTestCase(unittest.TestCase):
    def test_parse_changelog(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'release', 'fixtures')
        changelog_path = os.path.join(fixture_path, 'CHANGELOG.md')

        changelog = parse_changelog(changelog_path)

        self.assertEqual(changelog.name, 'swiftenv Changelog')
        self.assertEqual(len(changelog.releases), 2)
        self.assertEqual(changelog.releases[0].name, 'Master')
        self.assertEqual(changelog.releases[1].name, '1.0.0')

    def test_retrieves_last_changelog(self):
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'release', 'fixtures')
        changelog_path = os.path.join(fixture_path, 'BUMPED_CHANGELOG.md')
        changelog = extract_last_changelog(changelog_path)

        expected = '### Bug Fixes\n\n- `swiftenv uninstall` will now uninstall Swift toolchains on OS X.'
        self.assertEqual(changelog, expected)

    def test_retrieves_only_changelog(self):
        with temp_directory():
            touch('CHANGELOG.md', '# My Changelog\n## Current Release\n\nThe Release Information')
            changelog = extract_last_changelog('CHANGELOG.md')

        self.assertEqual(changelog, 'The Release Information')
