import os
import sys
import subprocess

import click
from git import Repo

from maintain.process import chdir


def gather_repositories():
    """
    Collects all of the repositories. The current implementation
    searches for them in the current working directory.
    """

    for (root, dirs, files) in os.walk('.'):
        basename = os.path.basename(root)

        if basename != '.git':
            continue

        path= os.path.split(root)[0]
        repo = os.path.basename(path)
        yield (repo, path)


@click.group()
def repo():
    pass


@repo.command('print')
def print_command():
    """
    Prints all repos.
    """

    for (repo, path) in gather_repositories():
        print(repo)


@repo.command()
@click.argument('command', nargs=-1)
@click.option('--exit/--no-exit', default=False)
@click.option('--silent/--no-silent', '-s', default=False)
def run(command, exit, silent):
    """
    Runs given command on all repos and checks status

        $ maintain repo run -- git checkout master
    """

    status = 0

    for (repo, path) in gather_repositories():
        with chdir(path):
            result = subprocess.run(command, shell=True, capture_output=silent)
            if result.returncode != 0:
                status = result.returncode

                print('Command failed: {}'.format(repo))

                if exit:
                    break

    sys.exit(status)
