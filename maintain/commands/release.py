import os
from glob import glob
import json
import collections
import subprocess

import click
from semantic_version import Version

from maintain.process import invoke


@click.command()
@click.argument('version')
def release(version):
    try:
        version = Version(version)
    except ValueError as e:
        click.echo('{} is not a valid semantic version.'.format(version), err=True)
        exit(1)

    all_releasers_cls = [CocoaPodsReleaser]
    releasers_cls = filter(lambda r: r.detect(), all_releasers_cls)
    releasers = map(lambda r: r(), releasers_cls)

    git_check_repository()
    git_check_branch()
    git_update()
    git_check_dirty()
    bump_version_file(version)
    map(lambda r: r.bump(version), releasers)
    invoke(['git', 'commit', '-a', '-m', 'Release {}'.format(version)])
    invoke(['git', 'tag', '-a', str(version), '-m', 'Release {}'.format(version)])

    if False:
        invoke(['git', 'push', 'origin', 'master'])
        invoke(['git', 'push', 'origin', str(version)])

    map(lambda r: r.release(), releasers)



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



def bump_version_file(version):
    if not os.path.exists('VERSION'):
        return

    with open('VERSION', 'w') as fp:
        fp.write(str(version))

