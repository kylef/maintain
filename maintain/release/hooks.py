import subprocess

from maintain.release.base import Releaser


class HookReleaser(Releaser):
    name = 'Hooks'

    @classmethod
    def detect(cls):
        raise NotImplemented

    @classmethod
    def from_config(cls, config):
        releaser = cls()

        if 'release' in config:
            releaser.pre_bump_commands = config['release'].get('bump', {}).get('pre', [])
            releaser.post_bump_commands = config['release'].get('bump', {}).get('post', [])
            releaser.pre_release_commands = config['release'].get('publish', {}).get('pre', [])
            releaser.post_release_commands = config['release'].get('publish', {}).get('post', [])

        return releaser

    def __init__(self):
        self.pre_bump_commands = []
        self.bump_commands = []
        self.post_bump_commands = []

        self.pre_release_commands = []
        self.release_commands = []
        self.post_release_commands = []

    def pre_bump(self, new_version):
        self.execute_hooks('pre bump', self.pre_bump_commands)

    def bump(self, new_version):
        self.execute_hooks('bump', self.bump_commands)

    def post_bump(self, new_version):
        self.execute_hooks('post bump', self.post_bump_commands)

    def pre_release(self, new_version):
        self.execute_hooks('pre release', self.pre_release_commands)

    def release(self, new_version):
        self.execute_hooks('release', self.release_commands)

    def post_release(self, new_version):
        self.execute_hooks('post release', self.post_release_commands)

    def execute_hooks(self, phase, commands):
        if len(commands) > 0:
            click.echo('Running {} hooks'.format(phase))

            for hook in commands:
                click.echo('- ' + hook)
                subprocess.check_output(hook, shell=True)
