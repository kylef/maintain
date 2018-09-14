import os

import jsonschema
import requests
import yaml

from maintain.release.aggregate import AggregateReleaser


SCHEMA = {
    'type': 'object',
    'properties': {
        'release': {
            'type': 'object',
            'properties': {},
            'patternProperties': {
                '': {
                    'type': 'object'
                }
            }
        }
    }
}


for releaser in AggregateReleaser.releasers():
    if not releaser.schema():
        continue

    SCHEMA['properties']['release']['properties'][releaser.config_name()] = releaser.schema()


class Configuration(object):
    @classmethod
    def load(cls):
        paths = [
            '.maintain.yml',
            '.maintain.yaml',
            os.path.join('.maintain', 'config.yml'),
            os.path.join('.maintain', 'config.yaml'),
        ]

        found_paths = list(filter(os.path.exists, paths))

        if len(found_paths) == 0:
            return cls()

        if len(found_paths) > 1:
            paths = ', '.join(found_paths)
            raise Exception('Multiple configuration files found: {}'.format(paths))

        return cls.fromfile(found_paths[0])

    @classmethod
    def fromurl(cls, url):
        if not url.startswith('https://'):
            raise Exception('Remote configuration reference {} must be https'.format(url))

        response = requests.get(url)
        response.raise_for_status()
        return yaml.load(response.text)

    @classmethod
    def fromfile(cls, path):
        with open(path) as fp:
            content = fp.read()
            content = yaml.load(content)

            if '$ref' in content:
                content = cls.fromurl(content['$ref'])

            cls.validate(content)

        return cls(**content)

    @classmethod
    def validate(cls, config):
        jsonschema.validate(config, SCHEMA)
        return True

    def __init__(self, release=None):
        self.release = release or {}
