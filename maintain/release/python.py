import os
import re

from semantic_version import Version

from maintain.release.base import Releaser
from maintain.process import invoke


class PythonReleaser(Releaser):
    name = 'Python'
    VERSION_REGEX = re.compile(r'version\s*=\s*["\'](.*)["\']')
    VERSION_SUB_REGEX = re.compile(r'(version\s*=\s*["\']).*(["\'])')

    @classmethod
    def detect(cls):
        return os.path.exists('setup.py')

    def determine_current_version(self):
        with open('setup.py') as fp:
            match = self.VERSION_REGEX.search(fp.read())
            if match:
                return Version(match.groups()[0])
            else:
                raise Exception('Invalid setup.py, doesn\'t contain a version.')

    def bump(self, new_version):
        with open('setup.py', 'r') as fp:
            def replace(matcher):
                return '{}{}{}'.format(matcher.group(1), new_version,
                                       matcher.group(2))

            content = self.VERSION_SUB_REGEX.sub(replace, fp.read(), count=1)

        with open('setup.py', 'w') as fp:
            fp.write(content)

    def release(self):
        version = self.determine_current_version()
        invoke(['python', 'setup.py', 'sdist', 'bdist_wheel'])
        invoke(['twine', 'upload', 'dist/*{}*'.format(version)])
