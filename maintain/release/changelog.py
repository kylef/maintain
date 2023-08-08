import os
import re
from datetime import date
from typing import Optional

from semantic_version import Version

from maintain.changelog import Changelog, parse_changelog
from maintain.release.base import Releaser


class ChangelogReleaser(Releaser):
    name = "changelog"
    path = "CHANGELOG.md"

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

    @classmethod
    def detect(cls) -> bool:
        return os.path.exists(cls.path)

    @classmethod
    def schema(cls):
        return {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "object",
                    "patternProperties": {
                        "": {"enum": [cls.MAJOR, cls.MINOR, cls.PATCH]},
                    },
                },
            },
            "additionalProperties": False,
        }

    def __init__(self, config=None) -> None:
        self.sections = {
            "breaking": "major",
            "enhancements": "minor",
            "bug fixes": "patch",
        }

        if config:
            sections = config.get("sections", {})
            if len(sections) > 0:
                self.sections = {}

                for section in sections:
                    self.sections[section.lower()] = sections[section]

        changelog = parse_changelog(self.path)
        self.validate_changelog(changelog)

    def validate_changelog(self, changelog: Changelog) -> None:
        for release in changelog.releases:
            found = []

            for section in release.sections:
                if section.name.lower() not in self.sections.keys():
                    raise Exception(
                        "Changelog section {} is not supported.".format(section.name)
                    )

                if section.name.lower() in found:
                    raise Exception(
                        "Changelog section {} is duplicated in release {}".format(
                            section.name, release.name
                        )
                    )

                found.append(section.name.lower())

    def determine_current_version(self) -> Optional[Version]:
        changelog = parse_changelog(self.path)
        for release in changelog.releases:
            if release.name == "Master":
                continue

            return Version(release.name)

        return None

    def determine_next_version(self) -> Optional[Version]:
        current_version = self.determine_current_version()
        assert current_version
        if current_version.prerelease or current_version.build:
            return None

        changelog = parse_changelog(self.path)

        for release in changelog.releases:
            if release.name != "Master":
                continue

            major = False
            minor = False
            patch = False

            for section in self.sections:
                if release.find_section(section):
                    if self.sections[section] == self.MAJOR:
                        major = True
                    elif self.sections[section] == self.MINOR:
                        minor = True
                    if self.sections[section] == self.PATCH:
                        patch = True

            if major:
                if current_version.major == 0:
                    return current_version.next_minor()

                return current_version.next_major()

            if minor:
                return current_version.next_minor()

            if patch:
                return current_version.next_patch()

        return None

    def bump(self, new_version: Version) -> None:
        changelog = parse_changelog(self.path)

        if len(changelog.releases) > 0:
            release = changelog.releases[0]
            if release.name == "Master":
                with open(self.path) as fp:
                    content = fp.read()

                heading = "## {} ({})".format(new_version, date.today().isoformat())
                content = re.sub(r"^## Master$", heading, content, flags=re.MULTILINE)

                with open("CHANGELOG.md", "w") as fp:
                    fp.write(content)
            else:
                raise Exception(
                    "Last changelog release was `{}` and not `Master`.".format(
                        release.name
                    )
                )
        else:
            raise Exception("Changelog is missing a master release.")

    def release(self, new_version: Version) -> None:
        pass
