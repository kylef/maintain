import os
from glob import glob
import json
import collections
import subprocess
import ConfigParser
from StringIO import StringIO

import click
from click.exceptions import MissingParameter
import yaml
from semantic_version import Version

from maintain.process import invoke, temp_directory, chdir
from maintain.release.version_file import VersionFileReleaser
from maintain.release.python import PythonReleaser
from maintain.release.cocoapods import CocoaPodsReleaser
from maintain.release.npm import NPMReleaser


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


    releasers = determine_releasers()

    if not version and bump:
        raise MissingParameter(param_hint='version', param_type='argument')
    elif version in ('major', 'minor', 'patch'):
        if bump:
            version = bump_version(releasers[0].determine_current_version(), version)
        else:
            releasers[0].determine_current_version()
    else:
        try:
            version = Version(version)
        except ValueError as e:
            click.echo('{} is not a valid semantic version.'.format(version), err=True)
            exit(1)

    if not bump:
        current_version = releasers[0].determine_current_version()
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

        map(lambda r: r.bump(version), releasers)
        click.echo('Committing and tagging {}'.format(version))
        message = 'Release {}'.format(version)
        invoke(['git', 'commit', '-a', '-m', message])

        if not dry_run:
            invoke(['git', 'push', 'origin', branch])
            if pull_request:
                invoke(['hub', 'pull-request', '-m', message])

    if not dry_run and not pull_request:
        invoke(['git', 'tag', '-a', str(version), '-m', 'Release {}'.format(version)])
        invoke(['git', 'push', 'origin', str(version)])

        map(lambda r: r.release(), releasers)

    if dependents and not pull_request and 'dependents' in config:
        # TODO dry run
        url = subprocess.check_output('git config --get remote.origin.url', shell=True).strip()
        map(lambda x: update_dependent(x, version, url), config['dependents'])


def determine_releasers():
    """
    Finds and initialises all of the releasers for the current project.
    """
    all_releasers_cls = [
        VersionFileReleaser,
        PythonReleaser,
        CocoaPodsReleaser,
        NPMReleaser
    ]
    releasers_cls = filter(lambda r: r.detect(), all_releasers_cls)
    releasers = map(lambda r: r(), releasers_cls)

    if len(releasers) == 0:
        click.echo('Project doesn\'t use any supported releasers.')
        exit(1)

    check_versions_are_same(releasers)
    return releasers


def check_versions_are_same(releasers):
    """
    Determine if any releasers have inconsistent versions
    """

    version = None
    releaser_name = None

    for releaser in releasers:
        next_version = releaser.determine_current_version()

        if version and version != next_version:
            click.echo('Inconsistent versions, {} is at {} but {} is at {}.'.format(
                       releaser_name, version, releaser.name, next_version))
            exit(1)

        version = next_version
        releaser_name = releaser.name


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
    parser = ConfigParser.SafeConfigParser()

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
    return subprocess.call('type {}'.format(cmd), shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


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

