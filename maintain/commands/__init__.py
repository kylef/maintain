import click

from maintain.config import Configuration
from maintain.commands.release import release
from maintain.commands.repo import repo


@click.group()
@click.option('--config', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    if config:
        ctx.obj = Configuration.fromfile(config)
    else:
        ctx.obj = Configuration.load()


cli.add_command(release)
cli.add_command(repo)
