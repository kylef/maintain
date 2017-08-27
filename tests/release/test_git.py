import unittest
import os
import shutil
import filecmp
import subprocess

from semantic_version import Version

from maintain.release.git import GitReleaser
from ..utils import temp_directory, touch


class GitReleaserTestCase(unittest.TestCase):
    # Detection

    def test_detects_git_repo(self):
        with temp_directory():
            self.assertFalse(GitReleaser.detect())
            subprocess.check_output('git init', shell=True)
            self.assertTrue(GitReleaser.detect())

    # Bump

    def test_bump_creates_release_commit_when_changes(self):
        with temp_directory():
            subprocess.check_output('git init', shell=True)

            touch('README.md')
            subprocess.check_output('git add README.md', shell=True)
            subprocess.check_output('git commit -m initial', shell=True)

            releaser = GitReleaser()

            touch('CHANGELOG.md')
            subprocess.check_output('git add CHANGELOG.md', shell=True)

            releaser.bump(Version('1.0.0'))

            log = subprocess.check_output('git log --format=oneline', shell=True).decode('utf-8')
            sha1, commit = log.split('\n')[0].split(' ', 1)
            self.assertEqual(commit, 'Release 1.0.0')

    def test_bump_without_changes(self):
        with temp_directory():
            subprocess.check_output('git init', shell=True)

            touch('README.md')
            subprocess.check_output('git add README.md', shell=True)
            subprocess.check_output('git commit -m initial', shell=True)

            GitReleaser().bump(Version('1.0.0'))

            log = subprocess.check_output('git log --format=oneline', shell=True).decode('utf-8')
            sha1, commit = log.split('\n')[0].split(' ', 1)
            self.assertEqual(commit, 'initial')
