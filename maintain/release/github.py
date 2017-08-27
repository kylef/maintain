import os
import subprocess

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.process import invoke


class GitHubReleaser(Releaser):
    name = 'GitHub'

    @classmethod
    def detect(cls):
        return os.path.exists('.git') and is_github_remote()

    def __init__(self):
        pass

    def determine_current_version(self):
        pass

    def bump(self, new_version):
        pass

    def release(self):
        pass


def is_github_remote():
    try:
        remote = subprocess.check_output('git remote get-url origin', shell=True).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return None

    return remote.startswith('https://github.com') or remote.startswith('git@github.com')
