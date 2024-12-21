import os
import unittest

from maintain.changelog import extract_last_changelog, parse_changelog
from tests.utils import temp_directory, touch


class ChangelogTestCase(unittest.TestCase):
    def test_parse_changelog(self):
        fixture_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "release", "fixtures"
        )
        changelog_path = os.path.join(fixture_path, "CHANGELOG.md")

        changelog = parse_changelog(changelog_path)

        self.assertEqual(changelog.name, "swiftenv Changelog")
        self.assertEqual(len(changelog.releases), 2)
        self.assertEqual(changelog.releases[0].name, "Master")
        self.assertEqual(changelog.releases[1].name, "1.0.0")

    def test_retrieves_last_changelog(self):
        fixture_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "release", "fixtures"
        )
        changelog_path = os.path.join(fixture_path, "BUMPED_CHANGELOG.md")
        changelog = extract_last_changelog(changelog_path)

        expected = "### Bug Fixes\n\n- `swiftenv uninstall` will now uninstall Swift toolchains on OS X."
        self.assertEqual(changelog, expected)

    def test_retrieves_only_changelog(self):
        with temp_directory():
            touch(
                "CHANGELOG.md",
                "# My Changelog\n## Current Release\n\nThe Release Information",
            )
            changelog = extract_last_changelog("CHANGELOG.md")

        self.assertEqual(changelog, "The Release Information")

    # Validation

    def test_disallows_multiple_h1s(self):
        with temp_directory():
            touch("CHANGELOG.md", "# My Changelog\n# Current Release\n")

            with self.assertRaisesRegex(
                Exception, "Changelog has multiple level 1 headings."
            ):
                parse_changelog("CHANGELOG.md")

    def test_disallows_missing_h1(self):
        with temp_directory():
            touch("CHANGELOG.md", "Hello World")

            with self.assertRaisesRegex(
                Exception,
                "Changelog does not start with a level 1 heading, including the changelog name.",
            ):
                parse_changelog("CHANGELOG.md")

    def test_disallows_heading_level_3_without_release(self):
        with temp_directory():
            touch("CHANGELOG.md", "# H1\n### H3\n")

            with self.assertRaisesRegex(
                Exception,
                r"Level 3 heading was not found within a release \(level 2 heading\)",
            ):
                parse_changelog("CHANGELOG.md")

    def test_disallows_heading_level_jump(self):
        with temp_directory():
            touch("CHANGELOG.md", "# H1\n#### H3\n")

            with self.assertRaisesRegex(
                Exception,
                "Changelog heading level jumps from level 1 to level 4. Must jump one level per heading.",
            ):
                parse_changelog("CHANGELOG.md")
