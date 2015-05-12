import json
import collections
from glob import glob

from maintain.release.base import Releaser
from maintain.process import invoke


class CocoaPodsReleaser(Releaser):
    name = 'CocoaPods'

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

        if not self.podspec.endswith('.json'):
            # TODO Add support for Ruby Podspecs
            raise Exception('Ruby podspecs are currently unsupported.')

    def bump(self, new_version):
        with open(self.podspec) as fp:
            spec = json.load(fp, object_pairs_hook=collections.OrderedDict)
            spec['version'] = new_version

        with open(self.podspec, 'w') as fp:
            json.dump(spec, fp, indent=2, separators=(',', ': '))
            fp.write('\n')

    def release(self):
        invoke(['pod', 'trunk', 'push', self.podspec])

