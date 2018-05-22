import unittest

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.release.aggregate import AggregateReleaser
from maintain.release.version_file import VersionFileReleaser
from ..utils import temp_directory, touch


class MockReleaser(Releaser):
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

    def release(self, new_version):
        self.is_released = True


class AggregateReleaserTestCase(unittest.TestCase):
    def test_errors_when_inconsistent_releaser_versions(self):
        releasers = [
            MockReleaser('1.2.3'),
            MockReleaser('1.2.4'),
        ]

        with self.assertRaises(Exception):
            AggregateReleaser(releasers=releasers)

    def test_detect_current_version(self):
        releaser = AggregateReleaser(releasers=[MockReleaser('1.2.3')])
        version = releaser.determine_current_version()
        self.assertEqual(version, Version('1.2.3'))

    def test_determine_next_version_unknown(self):
        releaser = AggregateReleaser(releasers=[
            MockReleaser('1.2.3'),
            MockReleaser('1.2.3'),
        ])
        version = releaser.determine_next_version()
        self.assertEqual(version, None)

    def test_determine_next_version(self):
        releaser = AggregateReleaser(releasers=[
            MockReleaser('1.2.3'),
            MockReleaser('1.2.3', '1.3.0'),
        ])
        version = releaser.determine_next_version()
        self.assertEqual(version, Version('1.3.0'))

    def test_determine_inconsistent_next_version(self):
        releaser = AggregateReleaser(releasers=[
            MockReleaser('1.2.3', '2.0.0'),
            MockReleaser('1.2.3', '1.3.0'),
        ])
        with self.assertRaises(Exception):
            releaser.determine_next_version()

    def test_bumping(self):
        releasers = [
            MockReleaser('1.2.3'),
            MockReleaser('1.2.3'),
        ]

        releaser = AggregateReleaser(releasers=releasers)
        releaser.bump('2.0.0')

        versions = map(lambda r: r.determine_current_version(), releasers)
        self.assertEqual(list(versions), [Version('2.0.0'), Version('2.0.0')])

    def test_releasing(self):
        releasers = [
            MockReleaser('1.2.3'),
            MockReleaser('1.2.3'),
        ]

        releaser = AggregateReleaser(releasers=releasers)
        releaser.release(None)

        released = list(map(lambda r: r.is_released, releasers))
        self.assertEqual(released, [True, True])

    def test_detecting_releasers(self):
        with temp_directory():
            touch('VERSION', '1.0.0\n')

            releaser = AggregateReleaser()
            releasers = list(filter(lambda r: isinstance(r, VersionFileReleaser), releaser.releasers))
            self.assertEqual(len(releasers), 1)

    def test_detecting_disabled_releasers(self):
        with temp_directory():
            touch('VERSION', '1.0.0\n')

            releaser = AggregateReleaser(config={
                'version_file': {
                    'disabled': True
                }
            })
            releasers = list(filter(lambda r: isinstance(r, VersionFileReleaser), releaser.releasers))
            self.assertEqual(len(releasers), 0)
