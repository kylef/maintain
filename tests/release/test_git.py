import unittest

from semantic_version import Version
from git import Repo

from maintain.release.git_releaser import GitReleaser
from ..utils import git_bare_repo, git_repo, touch, temp_directory


class GitReleaserTestCase(unittest.TestCase):
    # Initialisation

    def test_errors_when_non_master(self):
        with git_repo() as repo:
            touch('README.md')

            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.head.set_reference(repo.create_head('kylef', repo.head))

            with self.assertRaises(Exception):
                GitReleaser()

    def test_errors_when_unstaged_dirty(self):
        with git_repo() as repo:
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            with open('README.md', 'w') as fp:
                fp.write('Hello')

            with self.assertRaises(Exception):
                GitReleaser()

    def test_errors_when_staged_cache_dirty(self):
        with git_repo() as repo:
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            with open('README.md', 'w') as fp:
                fp.write('Hello')

            repo.index.add(['README.md'])

            with self.assertRaises(Exception):
                GitReleaser()

    def test_errors_when_untracked_files(self):
        with git_repo() as repo:
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            touch('HELLO')

            with self.assertRaises(Exception):
                GitReleaser()

    def test_errors_when_remote_has_changes(self):
        with git_bare_repo() as bare_repo:
            with git_repo() as repo:
                touch('README.md')
                repo.index.add(['README.md'])
                repo.index.commit('Initial commit')
                repo.create_remote('origin', url=bare_repo)
                repo.remotes.origin.push(repo.refs.master)

                with temp_directory() as path:
                    clone = Repo(bare_repo).clone(path)
                    touch('CHANGELOG.md')
                    clone.index.add(['README.md'])
                    clone.index.commit('Second commit')
                    clone.remotes.origin.push(clone.refs.master)

                with self.assertRaises(Exception):
                    GitReleaser()

    def test_init_with_remote(self):
        with git_bare_repo() as bare_repo:
            with git_repo() as repo:
                touch('README.md')
                repo.index.add(['README.md'])
                repo.index.commit('Initial commit')
                repo.create_remote('origin', url=bare_repo)
                repo.remotes.origin.push(repo.refs.master)

                GitReleaser()

    # Detection

    def test_detects_git_repo(self):
        with git_repo():
            self.assertTrue(GitReleaser.detect())

    # Bump

    def test_bump_creates_release_commit_when_changes(self):
        with git_repo() as repo:
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            releaser = GitReleaser()

            touch('CHANGELOG.md')
            repo.index.add(['CHANGELOG.md'])

            releaser.bump(Version('1.0.0'))

            self.assertEqual(repo.refs.master.commit.message, 'Release 1.0.0')

    def test_bump_without_changes(self):
        with git_repo() as repo:
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            GitReleaser().bump(Version('1.0.0'))

            self.assertEqual(repo.refs.master.commit.message, 'Initial commit')

    def test_bump_custom_commit_format(self):
        with git_repo() as repo:
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')

            releaser = GitReleaser(config={
                'commit_format': 'chore: Release {version}'
            })

            touch('CHANGELOG.md')
            repo.index.add(['CHANGELOG.md'])

            releaser.bump(Version('1.0.0'))

            self.assertEqual(repo.refs.master.commit.message, 'chore: Release 1.0.0')
