import click

from maintain.commands.release import release
from maintain.commands.repo import repo


@click.group()
def cli():
    pass


cli.add_command(release)
cli.add_command(repo)
