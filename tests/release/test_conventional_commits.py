import unittest

from maintain.release.conventional_commits import ConvetionalCommitsReleaser
from ..utils import git_repo, touch


class ConventionalCommitsReleaserTestCase(unittest.TestCase):
    # Detection

    def test_detects_git_repo(self):
        with git_repo():
            self.assertTrue(ConvetionalCommitsReleaser.detect())

    # Detect Current Version

    def test_detect_current_version(self):
        with git_repo() as repo:
            version = '1.0.0'
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.create_tag(version, message=version)

            version = '1.1.0'
            touch('TEST.md')
            repo.index.add(['TEST.md'])
            repo.index.commit('Second Commit')
            repo.create_tag(version, message=version)

            releaser = ConvetionalCommitsReleaser()
            current_version = releaser.determine_current_version()
            self.assertEqual(str(current_version), '1.1.0')

    # Detect Next Version

    def test_detect_next_version_patch(self):
        with git_repo() as repo:
            version = '1.0.0'
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.create_tag(version, message=version)

            touch('TEST.md')
            repo.index.add(['TEST.md'])
            repo.index.commit('fix: some bug')

            releaser = ConvetionalCommitsReleaser()
            current_version = releaser.determine_next_version()
            self.assertEqual(str(current_version), '1.0.1')

    def test_detect_next_version_minor(self):
        with git_repo() as repo:
            version = '1.0.0'
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.create_tag(version, message=version)

            touch('TEST.md')
            repo.index.add(['TEST.md'])
            repo.index.commit('feat: some bug')

            releaser = ConvetionalCommitsReleaser()
            current_version = releaser.determine_next_version()
            self.assertEqual(str(current_version), '1.1.0')

    def test_detect_next_version_major(self):
        with git_repo() as repo:
            version = '1.0.0'
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.create_tag(version, message=version)

            touch('TEST.md')
            repo.index.add(['TEST.md'])
            repo.index.commit('feat: some bug\n\nBREAKING CHANGE: This removes some flag')

            releaser = ConvetionalCommitsReleaser()
            current_version = releaser.determine_next_version()
            self.assertEqual(str(current_version), '2.0.0')

    def test_detect_next_version_various_commits(self):
        with git_repo() as repo:
            version = '1.0.0'
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.create_tag(version, message=version)

            touch('TEST.md')
            repo.index.add(['TEST.md'])
            repo.index.commit('fix: that awful bug')

            touch('TEST1.md')
            repo.index.add(['TEST1.md'])
            repo.index.commit('feat: awesome feature')

            touch('TEST2.md')
            repo.index.add(['TEST2.md'])
            repo.index.commit('fix: some other bug')

            releaser = ConvetionalCommitsReleaser()
            current_version = releaser.determine_next_version()
            self.assertEqual(str(current_version), '1.1.0')

    def test_detect_next_version_with_scope(self):
        with git_repo() as repo:
            version = '1.0.0'
            touch('README.md')
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            repo.create_tag(version, message=version)

            touch('TEST.md')
            repo.index.add(['TEST.md'])
            repo.index.commit('feat(scope): that awful bug')

            releaser = ConvetionalCommitsReleaser()
            current_version = releaser.determine_next_version()
            self.assertEqual(str(current_version), '1.1.0')
