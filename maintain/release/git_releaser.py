import os

from git import Repo

from maintain.release.base import Releaser
from maintain.process import invoke


class GitReleaser(Releaser):
    name = 'git'

    @classmethod
    def detect(cls):
        return os.path.exists('.git')

    def __init__(self):
        self.repo = Repo()

        if self.repo.head.ref != self.repo.heads.master:
            # TODO: Support releasing from stable/hotfix branches
            raise Exception('You need to be on the `master` branch in order to do a release.')

        if self.repo.is_dirty():
            raise Exception('Git repository has unstaged changes.')

        if self.has_origin():
            self.repo.remotes.origin.fetch()

            if self.repo.remotes.origin.refs.master.commit != self.repo.head.ref.commit:
                raise Exception('Master has unsynced changes.')

    def has_origin(self):
        try:
            self.repo.remotes.origin
        except AttributeError:
            return False

        return True

    def determine_current_version(self):
        return None

    def bump(self, new_version):
        if self.repo.is_dirty():
            message = 'Release {}'.format(new_version)
            self.repo.index.add('*')
            self.repo.index.commit(message)

    def release(self, version):
        tag = self.repo.create_tag(str(version), message='Release {}'.format(version))

        if self.has_origin():
            self.repo.remotes.origin.push(tag)


def git_update():
    invoke(['git', 'pull', 'origin', 'master'])
