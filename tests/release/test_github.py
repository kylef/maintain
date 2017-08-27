import unittest
import os
import shutil
import filecmp
import subprocess

from semantic_version import Version

from maintain.release.github import GitHubReleaser
from ..utils import temp_directory, touch


class GitHubReleaserTestCase(unittest.TestCase):
    def test_detect_https_github_remote(self):
        with temp_directory():
            subprocess.check_output('git init', shell=True)
            subprocess.check_output('git remote add origin https://github.com/kylef/maintain.git', shell=True)

            self.assertTrue(GitHubReleaser.detect())

    def test_detect_git_github_remote(self):
        with temp_directory():
            subprocess.check_output('git init', shell=True)
            subprocess.check_output('git remote add origin git@github.com:kylef/maintain.git', shell=True)

            self.assertTrue(GitHubReleaser.detect())

    def test_detect_without_git_repo(self):
        with temp_directory():
            self.assertFalse(GitHubReleaser.detect())

    def test_detect_without_github_remote(self):
        with temp_directory():
            subprocess.check_output('git init', shell=True)

            self.assertFalse(GitHubReleaser.detect())
