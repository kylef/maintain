import logging

from maintain.release.base import Releaser
from maintain.release.hooks import HookReleaser
from maintain.release.version_file import VersionFileReleaser
from maintain.release.python import PythonReleaser
from maintain.release.cocoapods import CocoaPodsReleaser
from maintain.release.npm import NPMReleaser
from maintain.release.c import CReleaser
from maintain.release.changelog import ChangelogReleaser
from maintain.release.git_releaser import GitReleaser
from maintain.release.github import GitHubReleaser


logger = logging.getLogger(__name__)


class AggregateReleaser(Releaser):
    @classmethod
    def releasers(cls):
        """
        Returns all of the supported releasers.
        """

        return [
            HookReleaser,
            VersionFileReleaser,
            PythonReleaser,
            CocoaPodsReleaser,
            NPMReleaser,
            CReleaser,
            ChangelogReleaser,
            GitReleaser,
            GitHubReleaser,
        ]

    @classmethod
    def detected_releasers(cls, config):
        """
        Returns all of the releasers that are compatible with the project.
        """

        def get_config(releaser):
            if config:
                return config.get(releaser.name.lower().replace(' ', '_'), {})

            return {}

        releasers = []

        for releaser_cls in cls.releasers():
            releaser_config = get_config(releaser_cls)

            if releaser_config.get('disabled', False):
                continue

            if releaser_cls.detect():
                logger.info('Enabled Releaser: {}'.format(releaser_cls.name))
                releasers.append(releaser_cls(releaser_config))

        return releasers

    @classmethod
    def detect(cls):
        return len(cls.detected_releasers()) > 0

    def __init__(self, config=None, releasers=None):
        self.releasers = releasers or self.detected_releasers(config)
        self.check_version_consistency()

    def check_version_consistency(self):
        """
        Determine if any releasers have inconsistent versions
        """

        version = None
        releaser_name = None

        for releaser in self.releasers:
            try:
                next_version = releaser.determine_current_version()
            except NotImplementedError:
                continue

            if next_version and version and version != next_version:
                raise Exception('Inconsistent versions, {} is at {} but {} is at {}.'.format(
                                releaser_name, version, releaser.name, next_version))

            version = next_version
            releaser_name = releaser.name

    def determine_current_version(self):
        for releaser in self.releasers:
            try:
                return releaser.determine_current_version()
            except NotImplementedError:
                continue

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
            releaser.pre_bump(new_version)

        for releaser in self.releasers:
            releaser.bump(new_version)

        for releaser in self.releasers:
            releaser.post_bump(new_version)

    def release(self, new_version):
        for releaser in self.releasers:
            releaser.pre_release(new_version)

        for releaser in self.releasers:
            releaser.release(new_version)

        for releaser in self.releasers:
            releaser.post_release(new_version)
