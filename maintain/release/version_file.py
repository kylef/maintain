import os

from semantic_version import Version

from maintain.release.base import Releaser


class VersionFileReleaser(Releaser):
    @classmethod
    def detect(cls):
        return os.path.exists('VERSION')

    def determine_current_version(self):
        with open('VERSION') as fp:
            return Version(fp.read().strip())

    def bump(self, new_version):
        with open('VERSION', 'w') as fp:
            fp.write(str(new_version) + '\n')

    def release(self):
        pass
