import os
import logging

from semantic_version import Version

from maintain.release.base import Releaser

logger = logging.getLogger(__name__)


class VersionFileReleaser(Releaser):
    name = 'Version File'

    @classmethod
    def detect(cls):
        return os.path.exists('VERSION')

    def determine_current_version(self):
        with open('VERSION') as fp:
            return Version(fp.read().strip())

    def bump(self, new_version):
        with open('VERSION', 'w') as fp:
            fp.write(str(new_version) + '\n')

        logger.info('Bumped VERSION file to {}'.format(new_version))

    def release(self, new_version):
        pass
