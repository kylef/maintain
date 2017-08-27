from git import Repo
from git.exc import InvalidGitRepositoryError

from maintain.release.base import Releaser


class GitHubReleaser(Releaser):
    name = 'GitHub'

    @classmethod
    def detect(cls):
        try:
            repo = Repo()
        except InvalidGitRepositoryError:
            return False

        try:
            url = repo.remotes.origin.url
        except AttributeError:
            return False

        return url.startswith('https://github.com') or url.startswith('git@github.com')

    def determine_current_version(self):
        pass

    def bump(self, new_version):
        pass

    def release(self):
        pass
