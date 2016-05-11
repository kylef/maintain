import json
import re
import collections
from glob import glob

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.process import invoke


class CocoaPodsReleaser(Releaser):
    name = 'CocoaPods'
    RUBY_VERSION_REGEX = re.compile(r'\.version\s*=\s*["\'](.*)["\']')
    RUBY_SUB_VERSION_REGEX = re.compile(r'(\.version\s*=\s*["\']).*(["\'])')

    @classmethod
    def podspecs(cls):
        """
        Returns all the podspecs in the project.
        """
        return glob('*.podspec') + glob('*.podspec.json')

    @classmethod
    def detect(cls):
        return len(cls.podspecs()) > 0

    def __init__(self):
        self.verify()

    def verify(self):
        podspecs = self.podspecs()

        if len(podspecs) > 1:
            raise Exception('Found multiple podspecs ({}), only one is' +
                            ' permitted.'.format(', '.join(podspecs)))

        self.podspec = podspecs[0]
        self.is_json_podspec = self.podspec.endswith('.json')

    def determine_current_version(self):
        with open(self.podspec) as fp:
            if self.is_json_podspec:
                return self.determine_current_version_json_podspec(fp)

            return self.determine_current_version_ruby_podspec(fp)

    def determine_current_version_json_podspec(self, fp):
        spec = json.load(fp)
        return Version(spec['version'])

    def determine_current_version_ruby_podspec(self, fp):
        match = self.RUBY_VERSION_REGEX.search(fp.read())
        if match:
            return Version(match.groups()[0])
        else:
            raise Exception('Invalid podspec ({}), doesn\'t contain ' +
                            'a version.'.format(self.podspec))

    def bump(self, new_version):
        if self.is_json_podspec:
            self.bump_json_podspec(new_version)
        else:
            self.bump_ruby_podspec(new_version)

    def bump_json_podspec(self, new_version):
        with open(self.podspec) as fp:
            spec = json.load(fp, object_pairs_hook=collections.OrderedDict)
            spec['version'] = str(new_version)
            source = spec['source']
            if 'tag' not in source:
                raise Exception('JSON podspec {} doesn\'t have a git ' +
                                'tag'.format(self.podspec))

            source['tag'] = str(new_version)
            spec['source'] = source

        with open(self.podspec, 'w') as fp:
            json.dump(spec, fp, indent=2, separators=(',', ': '))
            fp.write('\n')

    def bump_ruby_podspec(self, new_version):
        with open(self.podspec, 'r') as fp:
            def replace(matcher):
                return '{}{}{}'.format(matcher.group(1), new_version,
                                       matcher.group(2))

            content = self.RUBY_SUB_VERSION_REGEX.sub(replace, fp.read(), count=1)

        with open(self.podspec, 'w') as fp:
            fp.write(content)

    def release(self):
        invoke(['pod', 'trunk', 'push', self.podspec])
