import click

from maintain.commands.release import release


@click.group()
def cli():
    pass


cli.add_command(release)
