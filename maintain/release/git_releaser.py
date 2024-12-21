import logging
import os

from git import Repo
from semantic_version import Version

from maintain.git import get_default_branch
from maintain.process import invoke
from maintain.release.base import Releaser

logger = logging.getLogger(__name__)


class GitReleaser(Releaser):
    name = "git"

    @classmethod
    def detect(cls) -> bool:
        return os.path.exists(".git")

    @classmethod
    def schema(cls):
        return {
            "type": "object",
            "properties": {
                "commit_format": {"type": "string"},
                "tag_format": {"type": "string"},
            },
            "additionalProperties": False,
        }

    def __init__(self, config=None) -> None:
        self.repo = Repo()

        self.commit_format = (config or {}).get("commit_format", "Release {version}")
        self.tag_format = (config or {}).get("tag_format", "{version}")

        default_branch = get_default_branch(self.repo)

        if self.repo.head.ref != self.repo.heads[default_branch]:
            # TODO: Support releasing from stable/hotfix branches
            raise Exception(
                "You need to be on the default branch in order to do a release."
            )

        if self.repo.is_dirty():
            raise Exception("Git repository has unstaged changes.")

        if len(self.repo.untracked_files) > 0:
            raise Exception("Git repository has untracked files.")

        if self.has_origin():
            self.repo.remotes.origin.fetch()

            if self.repo.remotes.origin.refs[default_branch].commit != self.repo.head.ref.commit:
                raise Exception(f"{default_branch} has unsynced changes.")

    def has_origin(self) -> bool:
        try:
            self.repo.remotes.origin
        except AttributeError:
            return False

        return True

    def determine_current_version(self) -> None:
        return None

    def bump(self, new_version: Version) -> None:
        if self.repo.is_dirty():
            message = self.commit_format.format(version=new_version)

            self.repo.git.add(".")
            self.repo.index.commit(message)

            logger.info("Created Commit: {}".format(message))

    def release(self, version: Version) -> None:
        tag_name = self.tag_format.format(version=version)
        tag = self.repo.create_tag(tag_name, message="Release {}".format(version))

        logger.info("Created Tag: {}".format(tag_name))

        if self.has_origin():
            logger.info("Pushing Tag to Remote")
            self.repo.remotes.origin.push(tag)


def git_update() -> None:
    invoke(["git", "pull", "origin", "master"])
