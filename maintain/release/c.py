import re
from glob import glob

from semantic_version import Version

from maintain.release.base import Releaser


class CReleaser(Releaser):
    name = 'C'

    MAJOR_VERSION_REGEX = re.compile(r'\#define ([\w_]*)?VERSION_MAJOR (\d+)')
    MINOR_VERSION_REGEX = re.compile(r'\#define ([\w_]*)?VERSION_MINOR (\d+)')
    PATCH_VERSION_REGEX = re.compile(r'\#define ([\w_]*)?VERSION_PATCH (\d+)')

    SUB_MAJOR_VERSION_REGEX = re.compile(r'(\#define ([\w_]*)?VERSION_MAJOR )(\d+)')
    SUB_MINOR_VERSION_REGEX = re.compile(r'(\#define ([\w_]*)?VERSION_MINOR )(\d+)')
    SUB_PATCH_VERSION_REGEX = re.compile(r'(\#define ([\w_]*)?VERSION_PATCH )(\d+)')

    @classmethod
    def version_headers(cls):
        """
        Returns all the version headers in the project.
        """
        return glob('src/[Vv]ersion.h') + glob('include/*/[Vv]ersion.h')

    @classmethod
    def detect(cls):
        return len(cls.version_headers()) > 0

    def __init__(self):
        self.verify()

    def verify(self):
        headers = self.version_headers()

        if len(headers) > 1:
            raise Exception('Found multiple version headers ({}), only one' +
                            'is permitted.'.format(', '.join(headers)))

        self.header = headers[0]

    def determine_current_version(self):
        with open(self.header) as fp:
            contents = fp.read()

        major = self.MAJOR_VERSION_REGEX.search(contents)
        minor = self.MINOR_VERSION_REGEX.search(contents)
        patch = self.PATCH_VERSION_REGEX.search(contents)
        if major and minor and patch:
            version = '{}.{}.{}'.format(major.groups()[-1], minor.groups()[-1],
                                        patch.groups()[-1])
            return Version(version)
        else:
            raise Exception('Invalid version header ({}), doesn\'t contain ' +
                            'MAJOR, MINOR and PATCH versions.'.format(self.header))

    def bump(self, new_version):
        version = Version(new_version)

        if version.prerelease or version.build:
            raise Exception('Cannot bump prerelease or build in C projects.')

        with open(self.header) as fp:
            contents = fp.read()

        def replacer(component):
            def wrap(matcher):
                return '{}{}'.format(matcher.group(1), component)
            return wrap

        contents = self.SUB_MAJOR_VERSION_REGEX.sub(replacer(version.major), contents, count=1)
        contents = self.SUB_MINOR_VERSION_REGEX.sub(replacer(version.minor), contents, count=1)
        contents = self.SUB_PATCH_VERSION_REGEX.sub(replacer(version.patch), contents, count=1)

        with open(self.header, 'w') as fp:
            fp.write(contents)

    def release(self):
        pass
