import os
import re
from datetime import date
from collections import namedtuple

from semantic_version import Version
import CommonMark

from maintain.release.base import Releaser


class ChangelogReleaser(Releaser):
    @classmethod
    def detect(cls):
        return os.path.exists('CHANGELOG.md')

    def determine_current_version(self):
        changelog = parse_changelog()
        for release in changelog.releases:
            if release.name == 'Master':
                continue

            return Version(release.name)

    def bump(self, new_version):
        changelog = parse_changelog()

        if len(changelog.releases) > 0:
            release = changelog.releases[0]
            if release.name == 'Master':
                with open('CHANGELOG.md') as fp:
                    content = fp.read()

                heading = '## {} ({})'.format(new_version, date.today().isoformat())
                content = re.sub(r'^## Master$', heading, content, flags=re.MULTILINE)

                with open('CHANGELOG.md', 'w') as fp:
                    fp.write(content)
            else:
                raise Exception('Last changelog release was `{}` and not `Master`.'.format(release.name))
        else:
            raise Exception('Changelog is missing a master release.')

    def release(self):
        pass


class Changelog(object):
    def __init__(self, name, releases=None):
        self.name = name
        self.releases = releases or []


class Release(object):
    def __init__(self, name, release_date=None, sections=None):
        self.name = name
        self.release_date = release_date
        self.sections = sections or []


class Section(object):
    def __init__(self, name):
        self.name = name


def ast_to_headings(node):
    """
    Walks AST and returns a list of headings
    """

    Heading = namedtuple('Heading', ['level', 'title'])

    level = None
    walker = node.walker()
    headings = []

    event = walker.nxt()
    while event is not None:
        entering = event['entering']
        node = event['node']

        if node.t == 'Heading':
            if entering:
                level = node.level
            else:
                level = None
        elif level:
            if node.t != 'Text':
                raise Exception('Unexpected node {}, only text may be within a heading.'.format(node.t))

            headings.append(Heading(level=level, title=node.literal))

        event = walker.nxt()

    return headings


def ast_to_changelog(node):
    changelog = None
    headings = ast_to_headings(node)

    if len(headings) > 0 and headings[0].level == 1:
        changelog = Changelog(headings[0].title)
        headings = headings[1:]
    else:
        raise Exception('Changelog does not start with a level 1 heading, including the changelog name.')

    if any(map(lambda h: h.level == 1, headings)):
        raise Exception('Changelog has multiple level 1 headings.')

    release = None

    for heading in headings:
        if heading.level == 2:
            if release:
                changelog.releases.append(release)

            match = re.match(r'(\S+) \([\d\-]+\)', heading.title)
            if match:
                release = Release(match.groups()[0])
            else:
                release = Release(heading.title)
        elif heading.level == 3:
            if not release:
                raise Exception('Level 3 heading was not found within a release (level 2 heading).')

            release.sections.append(Section(heading.title))

    if release:
        changelog.releases.append(release)

    return changelog


def parse_changelog():
    with open('CHANGELOG.md', 'r') as fp:
        parser = CommonMark.Parser()
        ast = parser.parse(fp.read())
        return ast_to_changelog(ast)
