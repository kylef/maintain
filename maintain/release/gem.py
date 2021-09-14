import re
from glob import glob

from semantic_version import Version

from maintain.process import invoke
from maintain.release.base import Releaser


class GemReleaser(Releaser):
    name = 'Gem'
    VERSION_REGEX = re.compile(r'\.version\s*=\s*["\'](.*)["\']')
    VERSION_SUB_REGEX = re.compile(r'(\.version\s*=\s*["\']).*(["\'])')

    @classmethod
    def gemspecs(cls):
        return glob('*.gemspec')

    @classmethod
    def detect(cls) -> bool:
        return len(cls.gemspecs()) > 0

    def __init__(self) -> None:
        gemspecs = self.gemspecs()

        if len(gemspecs) > 1:
            raise Exception(('Found multiple gemspecs ({}), only one is' +
                            ' permitted.').format(', '.join(gemspecs)))

        self.gemspec = gemspecs[0]

    def determine_current_version(self) -> Version:
        with open(self.gemspec) as fp:
            match = self.VERSION_REGEX.search(fp.read())
            if match:
                return Version(match.groups()[0])
            else:
                raise Exception('Invalid gemspec, doesn\'t contain a version.')

    def bump(self, new_version: Version) -> None:
        with open(self.gemspec, 'r') as fp:
            def replace(matcher):
                return '{}{}{}'.format(matcher.group(1), new_version,
                                       matcher.group(2))

            content = self.VERSION_SUB_REGEX.sub(replace, fp.read(), count=1)

        with open(self.gemspec, 'w') as fp:
            fp.write(content)

    def release(self, new_version: Version) -> None:
        gems = glob('*.gem')
        if len(gems) != 0:
            raise Exception('Cannot release, found multiple unexpected ' +
                            'gems ({})'.format(', '.join(gems)))

        invoke(['gem', 'build', self.gemspec])
        invoke(['gem', 'push', glob('*.gem')[0]])
