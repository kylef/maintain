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


@repo.command()
@click.option('--exit/--no-exit', default=False)
def check(exit):
    status = 0

    for (name, path) in gather_repositories():
        with chdir(path):
            repo = Repo()
            failures = []

            if repo.head.ref != repo.heads.master:
                failures.append('Branch is not master')

            if repo.is_dirty():
                failures.append('Repository has unstaged changes')

            if len(repo.untracked_files) > 0:
                failures.append('Repository has untracked files')

            if repo.remotes.origin.refs.master.commit != repo.head.ref.commit:
                failures.append('Branch has unsynced changes')

            if len(failures) > 0:
                status = 1
                print(name)

                for failure in failures:
                    print(' - {}'.format(failure))

                if exit:
                    break

    sys.exit(status)
