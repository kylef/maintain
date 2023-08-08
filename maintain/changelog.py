import re
from collections import namedtuple
from typing import List, Optional

import commonmark


class Changelog(object):
    def __init__(self, name: str, releases=None) -> None:
        self.name = name
        self.releases = releases or []


class Section(object):
    def __init__(self, name: str) -> None:
        self.name = name


class Release(object):
    def __init__(self, name: str, release_date=None, sections=None) -> None:
        self.name = name
        self.release_date = release_date
        self.sections = sections or []

    def find_section(self, name: str) -> Optional[Section]:
        for section in self.sections:
            if section.name.lower() == name.lower():
                return section
        return None


Heading = namedtuple('Heading', ['level', 'title'])


def ast_to_headings(node) -> List[Heading]:
    """
    Walks AST and returns a list of headings
    """

    level = None
    walker = node.walker()
    headings = []

    event = walker.nxt()
    while event is not None:
        entering = event['entering']
        node = event['node']

        if node.t == 'heading':
            if entering:
                level = node.level
            else:
                level = None
        elif level:
            if node.t != 'text':
                raise Exception(
                    'Unexpected node {}, only text may be within a heading.'.format(
                        node.t
                    )
                )

            headings.append(Heading(level=level, title=node.literal))

        event = walker.nxt()

    return headings


def ast_to_changelog(node) -> Changelog:
    changelog = None
    headings = ast_to_headings(node)

    if len(headings) > 0 and headings[0].level == 1:
        changelog = Changelog(headings[0].title)
        headings = headings[1:]
    else:
        raise Exception(
            'Changelog does not start with a level 1 heading, including the changelog name.'
        )

    if any(map(lambda h: h.level == 1, headings)):
        raise Exception('Changelog has multiple level 1 headings.')

    release = None
    last_heading_level = 1

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
                raise Exception(
                    'Level 3 heading was not found within a release (level 2 heading).'
                )

            release.sections.append(Section(heading.title))

        if heading.level > last_heading_level + 1:
            raise Exception(
                'Changelog heading level jumps from level {} to level {}. Must jump one level per heading.'.format(
                    last_heading_level, heading.level
                )
            )
        last_heading_level = heading.level

    if release:
        changelog.releases.append(release)

    return changelog


def parse_changelog(path: str) -> Changelog:
    with open(path, 'r') as fp:
        parser = commonmark.Parser()
        ast = parser.parse(fp.read())
        return ast_to_changelog(ast)


def extract_last_changelog(path: str) -> Optional[str]:
    with open(path, 'r') as fp:
        parser = commonmark.Parser()
        content = fp.read()

    changelog = ast_to_changelog(parser.parse(content))

    if len(changelog.releases) == 0:
        raise Exception('No changelog releases')

    if len(changelog.releases) > 1:
        current = changelog.releases[0]
        previous = changelog.releases[1]

        with open(path, 'r') as fp:
            content = fp.read()

        pattern = r'\#\# {}(.*\n)([\n\S\s]*)\#\# {}'.format(
            re.escape(current.name), re.escape(previous.name)
        )
        result = re.search(pattern, content, re.MULTILINE)
        return result.group(2).strip()
    elif len(changelog.releases) == 1:
        current = changelog.releases[0]

        with open(path, 'r') as fp:
            content = fp.read()

        pattern = r'\#\# {}(.*\n)([\n\S\s]*)'.format(re.escape(current.name))
        result = re.search(pattern, content, re.MULTILINE)
        return result.group(2).strip()

    return None
