import os
import subprocess

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

import click
from click.exceptions import MissingParameter
import yaml
from semantic_version import Version

from maintain.process import invoke, temp_directory, chdir
from maintain.release.aggregate import AggregateReleaser
from maintain.release.git import GitReleaser
from maintain.release.github import GitHubReleaser


@click.command()
@click.argument('version', required=False)
@click.option('--dry-run/--no-dry-run', default=False)
@click.option('--bump/--no-bump', default=True)
@click.option('--pull-request/--no-pull-request', default=False)
def release(version, dry_run, bump, pull_request):
    if pull_request and not cmd_exists('hub'):
        click.echo('Missing dependency for hub: https://github.com/github/hub.' +
                   ' Please install `hub` and try again.')
        exit(1)

    if os.path.exists('.maintain.yml'):
        with open('.maintain.yml') as fp:
            config = yaml.load(fp.read())
    else:
        config = {}

    releaser = AggregateReleaser()

    if not GitHubReleaser.detect() and pull_request:
        raise Exception('Used --pull-request and no GitHub remote')

    if not version and bump:
        raise MissingParameter(param_hint='version', param_type='argument')
    elif version == 'semver':
        version = releaser.determine_next_version()
        if not version:
            raise Exception('Could not determine the next semantic version.')
    elif version in ('major', 'minor', 'patch'):
        if bump:
            version = bump_version(releaser.determine_current_version(), version)
        else:
            releaser.determine_current_version()
    else:
        try:
            version = Version(version)
        except ValueError:
            raise click.BadParameter('{} is not a semantic version'.format(version))

    if not bump:
        current_version = releaser.determine_current_version()
        if current_version != version:
            click.echo('--no-bump was used, however the supplied version ' +
                       'is not equal to current version {} != {}'.format(current_version, version))
            exit(1)

    git_releaser = GitReleaser()

    if bump:
        branch = 'master'
        if pull_request:
            branch = 'release-{}'.format(version)
            invoke(['git', 'checkout', '-b', branch])

        execute_hooks('bump', 'pre', config)

        releaser.bump(version)
        git_releaser.bump(version)

        execute_hooks('bump', 'post', config)

        if not dry_run:
            if git_has_origin_remote():
                invoke(['git', 'push', 'origin', branch])

            if pull_request:
                invoke(['hub', 'pull-request', '-m', message])

    if not dry_run and not pull_request:
        execute_hooks('publish', 'pre', config)

        git_releaser.release(version)
        releaser.release()

        execute_hooks('publish', 'post', config)


def bump_version(version, bump):
    if version.prerelease or version.build:
        print('Current version {} contains prerelease or build. ' +
              'Bumping is not supported.'.format(version))
        exit(1)

    return getattr(version, 'next_{}'.format(bump))()


def git_has_origin_remote():
    try:
        subprocess.check_output('git remote get-url origin', shell=True).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return False

    return True


def github_create_pr(message):
    invoke(['hub', 'pull-request', '-m', message])


def cmd_exists(cmd):
    result = subprocess.call('type {}'.format(cmd), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result == 0


def execute_hooks(phase, action, config):
    release_config = config.get('release', {})
    phase_config = release_config.get(phase, {})
    hooks = phase_config.get(action, [])

    if len(hooks) > 0:
        click.echo('Running {} {} hooks'.format(phase, action))

        for hook in hooks:
            click.echo('- ' + hook)
            subprocess.check_output(hook, shell=True)
