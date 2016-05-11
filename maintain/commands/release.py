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


@click.command()
@click.argument('version', required=False)
@click.option('--dry-run/--no-dry-run', default=False)
@click.option('--bump/--no-bump', default=True)
@click.option('--pull-request/--no-pull-request', default=False)
@click.option('--dependents/--no-dependents', default=True)
def release(version, dry_run, bump, pull_request, dependents):
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

    git_check_repository()
    git_check_branch()
    git_update()
    git_check_dirty()

    if bump:
        branch = 'master'
        if pull_request:
            branch = 'release-{}'.format(version)
            invoke(['git', 'checkout', '-b', branch])

        execute_hooks('bump', 'pre', config)

        releaser.bump(version)
        click.echo('Committing and tagging {}'.format(version))
        message = 'Release {}'.format(version)
        invoke(['git', 'commit', '-a', '-m', message])

        execute_hooks('bump', 'post', config)

        if not dry_run:
            invoke(['git', 'push', 'origin', branch])
            if pull_request:
                invoke(['hub', 'pull-request', '-m', message])

    if not dry_run and not pull_request:
        execute_hooks('publish', 'pre', config)

        invoke(['git', 'tag', '-a', str(version), '-m', 'Release {}'.format(version)])
        invoke(['git', 'push', 'origin', str(version)])

        releaser.release()

        execute_hooks('publish', 'post', config)

    if dependents and not pull_request and 'dependents' in config:
        # TODO dry run
        url = subprocess.check_output('git config --get remote.origin.url', shell=True).strip()
        map(lambda x: update_dependent(x, version, url), config['dependents'])


def bump_version(version, bump):
    if version.prerelease or version.build:
        print('Current version {} contains prerelease or build. ' +
              'Bumping is not supported.'.format(version))
        exit(1)

    return getattr(version, 'next_{}'.format(bump))()


def git_check_repository():
    if not os.path.exists('.git'):
        click.echo('release should be ran within a git repository')
        exit(1)


def git_update():
    invoke(['git', 'pull', '--no-rebase'])


def git_check_branch():
    branch = subprocess.check_output('git symbolic-ref HEAD 2>/dev/null', shell=True).strip().rpartition('/')[2]
    if branch != 'master':
        # TODO: Support releasing from stable/hotfix branches
        click.echo('You need to be on the `master` branch in order to do a release.')
        exit(1)


def git_check_dirty():
    error = 'You need to have a clean check out. You have un-committed local changes.'
    invoke(['git', 'diff', '--quiet'], error)
    invoke(['git', 'diff', '--cached'], error)


def git_load_config(filepath):
    parser = SafeConfigParser()

    with open(filepath) as fp:
        contents = ''.join([line.lstrip() for line in fp.readlines()])
        parser.readfp(StringIO(contents))

    return parser


def git_get_submodules():
    if os.path.exists('.gitmodules'):
        gitmodules = git_load_config('.gitmodules')

        def module(section):
            return (
                gitmodules.get(section, 'path'),
                gitmodules.get(section, 'url'),
            )

        return dict(map(module, gitmodules.sections()))


def github_create_pr(message):
    invoke(['hub', 'pull-request', '-m', message])


def cmd_exists(cmd):
    result = subprocess.call('type {}'.format(cmd), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result == 0


def update_dependent(dependent, version, source_url):
    with temp_directory():
        invoke(['git', 'clone', dependent, 'repository', '--depth', '1'])

        with chdir('repository'):
            # Check for submodules
            submodules = git_get_submodules()
            if not submodules:
                return  # TODO Only git submodules are supported

            module = next(iter(filter(lambda m: m[1] == source_url, submodules.items())), None)
            if not module:
                return

            invoke(['git', 'submodule', 'update', '--init'])

            with chdir(module[0]):
                invoke(['git', 'checkout', str(version)])

            # TODO branch name
            branch = 'update'
            invoke(['git', 'checkout', '-b', branch])

            # TODO commit message
            package = 'Unknown'
            message = '[{}] Update to {}'.format(package, version)
            invoke(['git', 'commit', '-a', '-m', message])
            invoke(['git', 'push', 'origin', branch])
            invoke(['hub', 'pull-request', '-m', message])


def execute_hooks(phase, action, config):
    release_config = config.get('release', {})
    phase_config = release_config.get(phase, {})
    hooks = phase_config.get(action, [])

    if len(hooks) > 0:
        click.echo('Running {} {} hooks'.format(phase, action))

        for hook in hooks:
            click.echo('- ' + hook)
            subprocess.check_output(hook, shell=True)
