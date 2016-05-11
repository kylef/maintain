import unittest

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.release.aggregate import AggregateReleaser


class TestReleaser(Releaser):
    def __init__(self, current_version, next_version=None):
        self.current_version = Version(current_version)
        if next_version:
            self.next_version = Version(next_version)
        else:
            self.next_version = None
        self.is_released = False

    def determine_current_version(self):
        return self.current_version

    def determine_next_version(self):
        return self.next_version

    def bump(self, new_version):
        self.current_version = Version(new_version)

    def release(self):
        self.is_released = True


class AggregateReleaserTestCase(unittest.TestCase):
    def test_errors_when_inconsistent_releaser_versions(self):
        releasers = [
            TestReleaser('1.2.3'),
            TestReleaser('1.2.4'),
        ]

        with self.assertRaises(Exception):
            AggregateReleaser(releasers=releasers)

    def test_detect_current_version(self):
        releaser = AggregateReleaser(releasers=[TestReleaser('1.2.3')])
        version = releaser.determine_current_version()
        self.assertEqual(version, Version('1.2.3'))

    def test_determine_next_version_unknown(self):
        releaser = AggregateReleaser(releasers=[
            TestReleaser('1.2.3'),
            TestReleaser('1.2.3'),
        ])
        version = releaser.determine_next_version()
        self.assertEqual(version, None)

    def test_determine_next_version(self):
        releaser = AggregateReleaser(releasers=[
            TestReleaser('1.2.3'),
            TestReleaser('1.2.3', '1.3.0'),
        ])
        version = releaser.determine_next_version()
        self.assertEqual(version, Version('1.3.0'))

    def test_determine_inconsistent_next_version(self):
        releaser = AggregateReleaser(releasers=[
            TestReleaser('1.2.3', '2.0.0'),
            TestReleaser('1.2.3', '1.3.0'),
        ])
        with self.assertRaises(Exception):
            releaser.determine_next_version()

    def test_bumping(self):
        releasers = [
            TestReleaser('1.2.3'),
            TestReleaser('1.2.3'),
        ]

        releaser = AggregateReleaser(releasers=releasers)
        releaser.bump('2.0.0')

        versions = map(lambda r: r.determine_current_version(), releasers)
        self.assertEqual(list(versions), [Version('2.0.0'), Version('2.0.0')])

    def test_releasing(self):
        releasers = [
            TestReleaser('1.2.3'),
            TestReleaser('1.2.3'),
        ]

        releaser = AggregateReleaser(releasers=releasers)
        releaser.release()

        released = list(map(lambda r: r.is_released, releasers))
        self.assertEqual(released, [True, True])
