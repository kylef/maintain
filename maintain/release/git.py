import os
import subprocess

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.process import invoke


class GitReleaser(Releaser):
    name = 'git'

    @classmethod
    def detect(cls):
        return os.path.exists('.git')

    def __init__(self):
        git_check_branch()

        if git_is_dirty():
            raise Exception('Git repository has unstaged changes.')

        if git_has_origin_remote():
            git_update()

    def determine_current_version(self):
        return None

    def bump(self, new_version):
        if git_is_dirty():
            message = 'Release {}'.format(new_version)
            invoke(['git', 'commit', '-a', '-m', message])

    def release(self, version):
        invoke(['git', 'tag', '-a', str(version), '-m', 'Release {}'.format(version)])

        if git_has_origin_remote():
            invoke(['git', 'push', 'origin', str(version)])


def git_update():
    invoke(['git', 'pull', 'origin', 'master', '--no-rebase'])


def git_check_branch():
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).decode('utf-8').strip()
    if branch != 'master':
        # TODO: Support releasing from stable/hotfix branches
        raise Exception('You need to be on the `master` branch in order to do a release.')


def git_is_dirty():
    if subprocess.call(['git', 'diff', '--quiet']) != 0:
        return True

    if subprocess.call(['git', 'diff', '--cached', '--quiet']) != 0:
        return True

    return False


def git_has_origin_remote():
    try:
        subprocess.check_output('git remote get-url origin', shell=True).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return False

    return True
