import unittest
import os

from click.testing import CliRunner
from git import Repo

from maintain.commands import cli
from maintain.process import chdir
from ..utils import temp_directory, git_bare_repo, touch


class eRepoommandTestCase(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_repo_print(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo1')
            Repo.init('repo2')
            Repo.init('repo3')

            result = self.runner.invoke(cli, ['repo', 'print'])

            repos = sorted(result.output.strip().split('\n'))

            self.assertEqual(repos, ['repo1', 'repo2', 'repo3'])
            self.assertEqual(result.exit_code, 0)

    # run

    def test_repo_run(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo1')
            Repo.init('repo2')

            result = self.runner.invoke(cli, ['repo', 'run', 'touch test'])

            self.assertEqual(result.output, '')
            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.exists('repo1/test'))
            self.assertTrue(os.path.exists('repo2/test'))

    def test_repo_run_exit_1(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo1')
            Repo.init('repo2')

            result = self.runner.invoke(cli, ['repo', 'run', 'false'])

            errors = sorted(result.output.strip().split('\n'))

            self.assertEqual(errors, ['Command failed: repo1', 'Command failed: repo2'])
            self.assertEqual(result.exit_code, 1)

    def test_repo_run_exit_early(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo1')
            Repo.init('repo2')

            result = self.runner.invoke(cli, ['repo', 'run', '--exit', 'false'])

            self.assertEqual(result.output, 'Command failed: repo1\n')
            self.assertEqual(result.exit_code, 1)

    def test_repo_run_check(self):
        with self.runner.isolated_filesystem():
            repo = Repo.init('repo1')
            touch('repo1/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            repo = Repo.init('repo2')
            touch('repo2/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            touch('repo1/dirty')

            result = self.runner.invoke(cli, ['repo', 'run', '--check', 'touch test'])

            self.assertEqual(result.output, 'repo1\n - Repository has untracked files\n')
            self.assertEqual(result.exit_code, 1)

            self.assertFalse(os.path.exists('repo1/test'))
            self.assertTrue(os.path.exists('repo2/test'))

    def test_repo_run_check_exit(self):
        with self.runner.isolated_filesystem():
            repo = Repo.init('repo1')
            touch('repo1/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            repo = Repo.init('repo2')
            touch('repo2/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            touch('repo1/dirty')

            result = self.runner.invoke(cli, ['repo', 'run', '--exit', '--check', 'touch test'])

            self.assertEqual(result.output, 'repo1\n - Repository has untracked files\n')
            self.assertEqual(result.exit_code, 1)

            self.assertFalse(os.path.exists('repo1/test'))
            self.assertFalse(os.path.exists('repo2/test'))


    # check

    def test_repo_check(self):
        with self.runner.isolated_filesystem():
            repo = Repo.init('repo')
            touch('repo/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            result = self.runner.invoke(cli, ['repo', 'check'])

            self.assertEqual(result.output, '')
            self.assertEqual(result.exit_code, 0)

    def test_repo_check_missing_master(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo')

            result = self.runner.invoke(cli, ['repo', 'check'])

            self.assertEqual(result.output, 'repo\n - Repository does not have a master branch\n')
            self.assertEqual(result.exit_code, 1)

    def test_repo_check_untracked_files(self):
        with self.runner.isolated_filesystem():
            repo = Repo.init('repo')
            touch('repo/README.md')
            touch('repo/CHANGELOG.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            result = self.runner.invoke(cli, ['repo', 'check'])

            self.assertEqual(result.output, 'repo\n - Repository has untracked files\n')
            self.assertEqual(result.exit_code, 1)

    def test_repo_check_unstaged_files(self):
        with self.runner.isolated_filesystem():
            repo = Repo.init('repo')
            touch('repo/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            with open('repo/README.md', 'w') as fp:
                fp.write('Hello')

            result = self.runner.invoke(cli, ['repo', 'check'])

            self.assertEqual(result.output, 'repo\n - Repository has unstaged changes\n')
            self.assertEqual(result.exit_code, 1)

    def test_repo_check_not_master(self):
        with self.runner.isolated_filesystem():
            repo = Repo.init('repo')
            touch('repo/README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.git.checkout('HEAD', b='stable/1')

            result = self.runner.invoke(cli, ['repo', 'check'])

            self.assertEqual(result.output, 'repo\n - Branch is not master\n')
            self.assertEqual(result.exit_code, 1)

    # cp

    def test_repo_cp(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo1')
            Repo.init('repo2')

            touch('README.md')

            result = self.runner.invoke(cli, ['repo', 'cp', 'README.md', 'README'])

            self.assertEqual(result.output, '')
            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.exists('repo1/README'))
            self.assertTrue(os.path.exists('repo2/README'))

    def test_repo_cp_error(self):
        with self.runner.isolated_filesystem():
            Repo.init('repo')
            touch('README.md')
            touch('repo/README.md')

            result = self.runner.invoke(cli, ['repo', 'cp', 'README.md', 'README.md'])

            self.assertEqual(result.output, 'Cannot copy to repo, README.md exists\n')
            self.assertEqual(result.exit_code, 1)
