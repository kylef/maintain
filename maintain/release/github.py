import os
import subprocess
import tempfile
from typing import Optional

from git import Repo
from git.exc import InvalidGitRepositoryError
from semantic_version import Version

from maintain.changelog import extract_last_changelog
from maintain.process import invoke
from maintain.release.base import Releaser


class GitHubReleaser(Releaser):
    name = "GitHub"

    @classmethod
    def detect(cls) -> bool:
        try:
            repo = Repo()
        except InvalidGitRepositoryError:
            return False

        try:
            url = repo.remotes.origin.url
        except AttributeError:
            return False

        return url.startswith("https://github.com") or url.startswith("git@github.com")

    @classmethod
    def schema(cls):
        return {
            "type": "object",
            "properties": {"artefacts": {"type": "array", "items": {"type": "string"}}},
            "additionalProperties": False,
        }

    def __init__(self, config):
        if not cmd_exists("hub"):
            raise Exception(
                "GitHub releases require hub. Missing dependency for hub: https://github.com/github/hub. Please install `hub` and try again."
            )

        self.artefacts = config.get("artefacts", [])

    def determine_current_version(self):
        pass

    def bump(self, new_version: Version) -> None:
        pass

    def release_command(self, new_version: Version):
        command = ["hub", "release", "create"]

        if new_version.prerelease:
            command.append("-p")

        for artefact in self.artefacts:
            command.append("-a")
            expanded_artefact = os.path.expandvars(artefact)
            command.append(expanded_artefact)

        command.append(str(new_version))

        return command

    def release(self, new_version: Version) -> None:
        command = self.release_command(new_version)

        changelog = self.get_changelog()
        if changelog:
            with tempfile.NamedTemporaryFile() as fp:
                fp.write("{}\n\n".format(new_version).encode("utf-8"))
                fp.write(changelog.encode("utf-8"))
                fp.flush()

                command.append("-F")
                command.append(fp.name)

                invoke(command)
            return

        invoke(command)

    def create_pull_request(self, version: Version) -> None:
        invoke(["hub", "pull-request", "-m", "Release {}".format(version)])

    def get_changelog(self) -> Optional[str]:
        if os.path.exists("CHANGELOG.md"):
            return extract_last_changelog("CHANGELOG.md")

        return None


def cmd_exists(cmd: str) -> bool:
    result = subprocess.call(
        "type {}".format(cmd),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result == 0
