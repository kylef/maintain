import os

import yaml
import jsonschema


SCHEMA = {
    'type': 'object',
    'properties': {
        'release': {
            'type': 'object',
            'patternProperties': {
                '': {
                    'type': 'object'
                }
            }
        }
    }
}


class Configuration(object):
    @classmethod
    def load(cls):
        paths = [
            '.maintain.yml',
            '.maintain.yaml',
            '.maintain/config.yml',
            '.maintain/config.yaml',
        ]

        found_paths = list(filter(os.path.exists, paths))

        if len(found_paths) == 0:
            return cls()

        if len(found_paths) > 1:
            paths = ', '.join(found_paths)
            raise Exception('Multiple configuration files found: {}'.format(paths))

        return cls.fromfile(found_paths[0])

    @classmethod
    def fromfile(cls, path):
        with open(path) as fp:
            content = fp.read()
            content = yaml.load(content)
            cls.validate(content)

        return cls(**content)

    @classmethod
    def validate(cls, config):
        jsonschema.validate(config, SCHEMA)
        return True

    def __init__(self, release=None):
        self.release = release or {}
