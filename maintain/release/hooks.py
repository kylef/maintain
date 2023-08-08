import logging
import os
import subprocess
from typing import List

from semantic_version import Version

from maintain.release.base import Releaser

logger = logging.getLogger(__name__)


class HookReleaser(Releaser):
    name = "Hooks"

    @classmethod
    def detect(cls) -> bool:
        return True

    @classmethod
    def schema(cls):
        hook = {
            "type": "object",
            "properties": {
                "pre": {"type": "array", "items": {"type": "string"}},
                "post": {"type": "array", "items": {"type": "string"}},
            },
        }
        return {
            "type": "object",
            "properties": {
                "bump": hook,
                "publish": hook,
            },
            "additionalProperties": False,
        }

    def __init__(self, config):
        self.bump_commands = []
        self.release_commands = []

        self.pre_bump_commands = config.get("bump", {}).get("pre", [])
        self.post_bump_commands = config.get("bump", {}).get("post", [])

        self.pre_release_commands = config.get("publish", {}).get("pre", [])
        self.post_release_commands = config.get("publish", {}).get("post", [])

    def pre_bump(self, new_version: Version) -> None:
        self.execute_hooks("pre_bump", self.pre_bump_commands, new_version)

    def bump(self, new_version: Version) -> None:
        self.execute_hooks("bump", self.bump_commands, new_version)

    def post_bump(self, new_version: Version) -> None:
        self.execute_hooks("post_bump", self.post_bump_commands, new_version)

    def pre_release(self, new_version: Version) -> None:
        self.execute_hooks("pre_release", self.pre_release_commands, new_version)

    def release(self, new_version: Version) -> None:
        self.execute_hooks("release", self.release_commands, new_version)

    def post_release(self, new_version: Version) -> None:
        self.execute_hooks("post_release", self.post_release_commands, new_version)

    def execute_hooks(self, phase: str, commands: List[str], version: Version) -> None:
        if len(commands) > 0:
            logger.info("Running {} hooks".format(phase))

            for hook in commands:
                logger.info("$ {}".format(hook))
                subprocess.check_output(hook, shell=True, env={"VERSION": version})

        hook_file = "./.maintain/hooks/{}".format(phase)

        if os.path.exists(hook_file) and os.access(hook_file, os.X_OK):
            subprocess.check_output(hook_file, shell=True, env={"VERSION": version})
