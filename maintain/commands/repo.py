import os
import subprocess
import sys
from shutil import copyfile

import click
from git import Repo

from maintain.process import chdir
from maintain.git import get_default_branch


def gather_repositories():
    """
    Collects all of the repositories. The current implementation
    searches for them in the current working directory.
    """

    for root, dirs, files in os.walk(".", topdown=True):
        dirs.sort()

        if ".git" not in dirs:
            continue

        for dir in list(dirs):
            dirs.remove(dir)

        path = os.path.split(root)[1]
        repo = os.path.basename(path)
        yield (repo, root)


def check_repo(name: str, path: str) -> bool:
    repo = Repo(path)
    failures = []

    try:
        default_branch = get_default_branch(repo)

        if repo.head.ref != repo.heads[default_branch]:
            failures.append(f"Current branch is not default branch ({default_branch})")

        if "origin" in repo.remotes:
            if repo.remotes.origin.refs[default_branch].commit != repo.head.ref.commit:
                failures.append("Branch has unsynced changes")
    except Exception as e:
        failures.append(str(e))

    if repo.is_dirty():
        failures.append("Repository has unstaged changes")

    if len(repo.untracked_files) > 0:
        failures.append("Repository has untracked files")

    if len(failures) > 0:
        click.echo(name)

        for failure in failures:
            click.echo(" - {}".format(failure))

    return len(failures) == 0


@click.group()
def repo() -> None:
    pass


@repo.command("print")
def print_command() -> None:
    """
    Prints all repos.
    """

    for repo, path in gather_repositories():
        click.echo(repo)


@repo.command()
@click.argument("command", nargs=-1)
@click.option("--exit/--no-exit", default=False)
@click.option("--silent/--no-silent", "-s", default=False)
@click.option("--check/--no-check", default=False)
def run(command, exit: bool, silent: bool, check: bool):
    """
    Runs given command on all repos and checks status

        $ maintain repo run -- git checkout master
    """

    status = 0

    for repo, path in gather_repositories():
        if check and not check_repo(repo, path):
            status = 1

            if exit:
                break

            continue

        with chdir(path):
            result = subprocess.run(command, shell=True, capture_output=silent)
            if result.returncode != 0:
                status = result.returncode

                print("Command failed: {}".format(repo))

                if exit:
                    break

    sys.exit(status)


@repo.command("check")
@click.option("--exit/--no-exit", default=False)
def check_command(exit: bool) -> None:
    status = 0

    for name, path in gather_repositories():
        if not check_repo(name, path):
            status = 1

            if exit:
                break

    sys.exit(status)


@repo.command()
@click.argument("src", nargs=-1, type=click.Path(exists=True))
@click.argument("dst", nargs=1, type=click.Path())
def cp(src, dst: str) -> None:
    status = 0

    for repo, path in gather_repositories():
        for filename in src:
            destination = os.path.join(path, dst)

            if os.path.exists(destination):
                status = 1
                print("Cannot copy to {}, {} exists".format(repo, dst))
                continue

            copyfile(filename, destination)

    sys.exit(status)
