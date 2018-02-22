import os
import re
from datetime import date

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.changelog import parse_changelog


class ChangelogReleaser(Releaser):
    path = 'CHANGELOG.md'

    @classmethod
    def detect(cls):
        return os.path.exists(cls.path)

    def determine_current_version(self):
        changelog = parse_changelog(self.path)
        for release in changelog.releases:
            if release.name == 'Master':
                continue

            return Version(release.name)

    def determine_next_version(self):
        current_version = self.determine_current_version()
        if current_version.prerelease or current_version.build:
            return None

        changelog = parse_changelog(self.path)

        for release in changelog.releases:
            if release.name != 'Master':
                continue

            breaking = release.find_section('Breaking')
            enhancements = release.find_section('Enhancements')
            bug_fixes = release.find_section('Bug Fixes')

            if breaking and current_version.major == 0:
                return current_version.next_minor()

            if breaking:
                return current_version.next_major()

            if enhancements:
                return current_version.next_minor()

            if bug_fixes:
                return current_version.next_patch()

        return None

    def bump(self, new_version):
        changelog = parse_changelog(self.path)

        if len(changelog.releases) > 0:
            release = changelog.releases[0]
            if release.name == 'Master':
                with open(self.path) as fp:
                    content = fp.read()

                heading = '## {} ({})'.format(new_version, date.today().isoformat())
                content = re.sub(r'^## Master$', heading, content, flags=re.MULTILINE)

                with open('CHANGELOG.md', 'w') as fp:
                    fp.write(content)
            else:
                raise Exception('Last changelog release was `{}` and not `Master`.'.format(release.name))
        else:
            raise Exception('Changelog is missing a master release.')

    def release(self, new_version):
        pass
