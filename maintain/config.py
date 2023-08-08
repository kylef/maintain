import os

import jsonschema
import yaml

from maintain.release.aggregate import AggregateReleaser

SCHEMA = {
    'type': 'object',
    'properties': {
        'release': {
            'type': 'object',
            'properties': {},
            'patternProperties': {'': {'type': 'object'}},
        }
    },
}


for releaser in AggregateReleaser.releasers():
    if not releaser.schema():
        continue

    SCHEMA['properties']['release']['properties'][
        releaser.config_name()
    ] = releaser.schema()


class Configuration(object):
    @classmethod
    def load(cls) -> 'Configuration':
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
            p = ', '.join(found_paths)
            raise Exception('Multiple configuration files found: {}'.format(p))

        return cls.fromfile(found_paths[0])

    @classmethod
    def fromfile(cls, path: str) -> 'Configuration':
        with open(path) as fp:
            content = fp.read()
            config = yaml.safe_load(content)
            cls.validate(config)

        return cls(**config)

    @classmethod
    def validate(cls, config) -> bool:
        jsonschema.validate(config, SCHEMA)
        return True

    def __init__(self, release=None):
        self.release = release or {}
