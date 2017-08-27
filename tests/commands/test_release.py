import unittest

from click.testing import CliRunner
from git import Repo

from maintain.commands.release import release
from ..utils import temp_directory, git_bare_repo


class ReleaseCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_requires_version_with_bump(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(release, [])

            self.assertTrue('Error: Missing argument version.' in result.output)
            self.assertEqual(result.exit_code, 2)

    def test_version_must_be_semantic_version(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(release, ['foo'])

            self.assertTrue('Error: Invalid value: foo is not a semantic version' in result.output, result.output)
            self.assertEqual(result.exit_code, 2)

    def test_git_release_without_remote(self):
        with self.runner.isolated_filesystem():
            with open('VERSION', 'w') as fp:
                fp.write('1.0.0\n')

            repo = Repo.init()
            repo.index.add(['VERSION'])
            repo.index.commit('Initial commit')

            result = self.runner.invoke(release, ['2.0.0'])
            self.assertIsNone(result.exception)
            self.assertEqual(result.exit_code, 0)

            with open('VERSION') as fp:
                self.assertEqual(fp.read(), '2.0.0\n')

            self.assertEqual(repo.refs.master.commit.message, 'Release 2.0.0')
            self.assertEqual(repo.tags['2.0.0'].commit, repo.refs.master.commit)
            self.assertFalse(repo.is_dirty())

    def test_git_release_with_remote(self):
        with git_bare_repo() as bare_repo:
            with temp_directory():
                with open('VERSION', 'w') as fp:
                    fp.write('1.0.0\n')

                repo = Repo.init()
                repo.index.add(['VERSION'])
                repo.index.commit('Initial commit')
                repo.create_remote('origin', url=bare_repo)
                repo.remotes.origin.push(repo.refs.master)

                result = self.runner.invoke(release, ['2.0.0'])
                self.assertIsNone(result.exception)
                self.assertEqual(result.exit_code, 0)

                with open('VERSION') as fp:
                    self.assertEqual(fp.read(), '2.0.0\n')

                self.assertEqual(repo.refs.master.commit.message, 'Release 2.0.0')
                self.assertEqual(repo.tags['2.0.0'].commit, repo.refs.master.commit)
                self.assertFalse(repo.is_dirty())

            bare_repo = Repo(bare_repo)
            self.assertEqual(bare_repo.commit('master').message, 'Release 2.0.0')
            self.assertEqual(bare_repo.tags['2.0.0'].commit, bare_repo.refs.master.commit)
