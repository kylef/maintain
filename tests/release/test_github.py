import os
import unittest

from semantic_version import Version

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

        with self.assertRaisesRegex(Exception, "GitHub releases require hub"):
            os.environ["PATH"] = "/tmp"
            GitHubReleaser(config={})

        os.environ["PATH"] = path

    def test_initialisation_with_hub(self):
        old_path = os.environ["PATH"]

        with temp_directory() as path:
            os.environ["PATH"] = path
            touch("hub")
            os.chmod("hub", 755)

            GitHubReleaser(config={})

        os.environ["PATH"] = old_path

    # Release

    def test_release_hub_command(self):
        releaser = GitHubReleaser(config={})

        command = releaser.release_command(Version("1.0.0"))

        self.assertEqual(command, ["hub", "release", "create", "1.0.0"])

    def test_release_hub_command_prerelease(self):
        releaser = GitHubReleaser(config={})

        command = releaser.release_command(Version("1.0.0-rc.1"))

        self.assertEqual(command, ["hub", "release", "create", "-p", "1.0.0-rc.1"])

    def test_release_hub_command_artefact(self):
        releaser = GitHubReleaser(
            config={
                "artefacts": [
                    "build.tar.xz",
                ],
            }
        )

        command = releaser.release_command(Version("1.0.0"))

        self.assertEqual(
            command, ["hub", "release", "create", "-a", "build.tar.xz", "1.0.0"]
        )

    def test_release_hub_command_artefact_version_substitute(self):
        releaser = GitHubReleaser(
            config={
                "artefacts": [
                    "build-$VERSION.tar.xz",
                ],
            }
        )

        os.environ["VERSION"] = "1.0.0"
        command = releaser.release_command(Version("1.0.0"))

        self.assertEqual(
            command, ["hub", "release", "create", "-a", "build-1.0.0.tar.xz", "1.0.0"]
        )
