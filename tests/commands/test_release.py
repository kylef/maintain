import unittest
import subprocess

from click.testing import CliRunner

from maintain.commands.release import release
from ..utils import temp_directory, touch, git_bare_repo


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

            self.assertTrue('Error: Invalid value: foo is not a semantic version' in result.output)
            self.assertEqual(result.exit_code, 2)

    def test_git_release_without_remote(self):
        with self.runner.isolated_filesystem():
            with open('VERSION', 'w') as fp:
                fp.write('1.0.0\n')

            subprocess.check_output('git init', shell=True)
            subprocess.check_output('git add VERSION', shell=True)
            subprocess.check_output('git commit -m One', shell=True)

            result = self.runner.invoke(release, ['2.0.0'])
            self.assertEqual(result.exit_code, 0)

            with open('VERSION') as fp:
                self.assertEqual(fp.read(), '2.0.0\n')

            # Created Commit
            log = subprocess.check_output('git log --format=oneline', shell=True).decode('utf-8')
            sha1, commit = log.split('\n')[0].split(' ', 1)
            self.assertEqual(commit, 'Release 2.0.0')

            # Created Tag
            tags = subprocess.check_output('git tag', shell=True).decode('utf-8').split('\n')
            self.assertEqual(tags[0], '2.0.0')

            # No Staged Changes
            subprocess.check_output('git diff --quiet', shell=True)
            subprocess.check_output('git diff --cached --quiet', shell=True)

    def test_git_release_with_remote(self):
        with git_bare_repo() as repo:
            with temp_directory():
                with open('VERSION', 'w') as fp:
                    fp.write('1.0.0\n')

                subprocess.check_output('git init', shell=True)
                subprocess.check_output('git remote add origin {}'.format(repo), shell=True)
                subprocess.check_output('git add VERSION', shell=True)
                subprocess.check_output('git commit -m One', shell=True)
                subprocess.check_output('git push origin master', shell=True)

                result = self.runner.invoke(release, ['2.0.0'])
                self.assertEqual(result.exit_code, 0)

                with open('VERSION') as fp:
                    self.assertEqual(fp.read(), '2.0.0\n')

                # Created Commit
                log = subprocess.check_output('git log --format=oneline', shell=True).decode('utf-8')
                sha1, commit = log.split('\n')[0].split(' ', 1)
                self.assertEqual(commit, 'Release 2.0.0')

                # Created Tag
                tags = subprocess.check_output('git tag', shell=True).decode('utf-8').split('\n')
                self.assertEqual(tags[0], '2.0.0')

                # No Staged Changes
                subprocess.check_output('git diff --quiet', shell=True)
                subprocess.check_output('git diff --cached --quiet', shell=True)

            # Pushed Commit
            log = subprocess.check_output('git --git-dir={} log --format=oneline'.format(repo), shell=True).decode('utf-8')
            sha1, commit = log.split('\n')[0].split(' ', 1)
            self.assertEqual(commit, 'Release 2.0.0')

            # Pushed Tag
            tags = subprocess.check_output('git --git-dir={} tag'.format(repo), shell=True).decode('utf-8').split('\n')
            self.assertEqual(tags[0], '2.0.0')
