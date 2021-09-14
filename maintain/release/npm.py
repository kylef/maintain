import collections
import json
import os

from semantic_version import Version

from maintain.process import invoke
from maintain.release.base import Releaser


class NPMReleaser(Releaser):
    name = 'npm'

    @classmethod
    def detect(cls):
        return os.path.exists('package.json')

    def determine_current_version(self):
        with open('package.json') as fp:
            spec = json.load(fp, object_pairs_hook=collections.OrderedDict)
            return Version(spec['version'])

    def bump(self, new_version):
        with open('package.json') as fp:
            spec = json.load(fp, object_pairs_hook=collections.OrderedDict)
            spec['version'] = str(new_version)

        with open('package.json', 'w') as fp:
            json.dump(spec, fp, indent=2, separators=(',', ': '))
            fp.write('\n')

    def release(self, new_version):
        invoke(['npm', 'publish'])
