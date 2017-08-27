import unittest

from maintain.release.github import GitHubReleaser
from ..utils import temp_directory, git_repo


class GitHubReleaserTestCase(unittest.TestCase):
    def test_detect_without_git_repo(self):
        with temp_directory():
            self.assertFalse(GitHubReleaser.detect())

    def test_detect_https_github_remote(self):
        with git_repo() as repo:
            repo.create_remote('origin', url='https://github.com/kylef/maintain.git')
            self.assertTrue(GitHubReleaser.detect())

    def test_detect_git_github_remote(self):
        with git_repo() as repo:
            repo.create_remote('origin', url='https://github.com/kylef/maintain.git')
            self.assertTrue(GitHubReleaser.detect())

    def test_detect_without_remote(self):
        with git_repo():
            self.assertFalse(GitHubReleaser.detect())

    def test_detect_without_github_remote(self):
        with git_repo() as repo:
            repo.create_remote('origin', url='https://fuller.li/maintain.git')
            self.assertFalse(GitHubReleaser.detect())
