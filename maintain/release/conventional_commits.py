import os
import re

from semantic_version import Version
from git import Repo, TagReference

from maintain.release.base import Releaser


class ConvetionalCommitsReleaser(Releaser):
    name = 'Conventional Commits'

    @classmethod
    def detect(cls):
        return os.path.exists('.git')

    def __init__(self):
        self.repo = Repo()

    def determine_current_version(self):
        tags = TagReference.list_items(self.repo)
        versions = [Version(tag.tag.tag) for tag in tags]
        return next(reversed(sorted(versions)))

    def determine_next_version(self):
        current_version = self.determine_current_version()

        if current_version.prerelease or current_version.build:
            return None

        breaking = 0
        feats = 0
        fixes = 0

        pattern = re.compile(r'^((\w+)(?:\(([^\)\s]+)\))?: (.+))+', re.MULTILINE)

        commits = self.repo.iter_commits('master...{}'.format(current_version))
        for commit in commits:
            if 'BREAKING CHANGE:' in commit.message:
                breaking += 1

            result = pattern.search(commit.message.strip())
            if result:
                typ = result.group(2)
                if typ == 'feat':
                    feats += 1
                elif typ == 'fix':
                    fixes += 1
                else:
                    raise Exception('Commit "{}" uses unsupported type {}'.format(commit, typ))
            else:
                raise Exception('Commit "{}" does not follow conventional commit'.format(commit))

        if breaking > 0:
            return current_version.next_major()
        elif feats > 0:
            return current_version.next_minor()
        elif fixes > 0:
            return current_version.next_patch()
