from maintain.release.base import Releaser
from maintain.release.version_file import VersionFileReleaser
from maintain.release.python import PythonReleaser
from maintain.release.cocoapods import CocoaPodsReleaser
from maintain.release.npm import NPMReleaser
from maintain.release.c import CReleaser
from maintain.release.changelog import ChangelogReleaser


class AggregateReleaser(Releaser):
    @classmethod
    def releasers(cls):
        """
        Returns all of the supported releasers.
        """

        return [
            VersionFileReleaser,
            PythonReleaser,
            CocoaPodsReleaser,
            NPMReleaser,
            CReleaser,
            ChangelogReleaser,
        ]

    @classmethod
    def detected_releasers(cls):
        """
        Returns all of the releasers that are compatible with the project.
        """

        releasers_cls = filter(lambda r: r.detect(), cls.releasers())
        releasers = map(lambda r: r(), releasers_cls)
        return releasers

    @classmethod
    def detect(cls):
        return len(cls.detected_releasers()) > 0

    def __init__(self, releasers=None):
        self.releasers = releasers or self.detected_releasers()
        self.check_version_consistency()

    def check_version_consistency(self):
        """
        Determine if any releasers have inconsistent versions
        """

        version = None
        releaser_name = None

        for releaser in self.releasers:
            next_version = releaser.determine_current_version()

            if next_version and version and version != next_version:
                raise Exception('Inconsistent versions, {} is at {} but {} is at {}.'.format(
                                releaser_name, version, releaser.name, next_version))

            version = next_version
            releaser_name = releaser.name

    def determine_current_version(self):
        return self.releasers[0].determine_current_version()

    def determine_next_version(self):
        version = None
        releaser_name = None

        for releaser in self.releasers:
            next_version = releaser.determine_next_version()
            if not next_version:
                continue

            if version and version != next_version:
                raise Exception('Inconsistent next versions, {} is at {} but {} is at {}.'.format(
                                releaser_name, version, releaser.name, next_version))

            version = next_version
            releaser_name = releaser.name

        return version

    def bump(self, new_version):
        for releaser in self.releasers:
            releaser.bump(new_version)

    def release(self):
        for releaser in self.releasers:
            releaser.release()
