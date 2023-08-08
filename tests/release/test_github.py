import os
import unittest

from maintain.release.github import GitHubReleaser

from ..utils import git_repo, temp_directory, touch


class GitHubReleaserTestCase(unittest.TestCase):
    # Detect

    def test_detect_without_git_repo(self):
        with temp_directory():
            self.assertFalse(GitHubReleaser.detect())

    def test_detect_https_github_remote(self):
        with git_repo() as repo:
            repo.create_remote("origin", url="https://github.com/kylef/maintain.git")
            self.assertTrue(GitHubReleaser.detect())

    def test_detect_git_github_remote(self):
        with git_repo() as repo:
            repo.create_remote("origin", url="https://github.com/kylef/maintain.git")
            self.assertTrue(GitHubReleaser.detect())

    def test_detect_without_remote(self):
        with git_repo():
            self.assertFalse(GitHubReleaser.detect())

    def test_detect_without_github_remote(self):
        with git_repo() as repo:
            repo.create_remote("origin", url="https://fuller.li/maintain.git")
            self.assertFalse(GitHubReleaser.detect())

    # Initialisation

    def test_initialisation_without_hub(self):
        path = os.environ["PATH"]

        with self.assertRaisesRegexp(Exception, "GitHub releases require hub"):
            os.environ["PATH"] = "/tmp"
            GitHubReleaser(config={})

        os.environ["PATH"] = path

    def test_initialisation_with_hub(self):
        with temp_directory() as path:
            os.environ["PATH"] = path
            touch("hub")
            os.chmod("hub", 755)

            GitHubReleaser(config={})
