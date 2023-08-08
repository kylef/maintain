import click

from maintain.commands.release import release
from maintain.commands.repo import repo
from maintain.config import Configuration


@click.group()
@click.option("--config", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config: str) -> None:
    if config:
        ctx.obj = Configuration.fromfile(config)
    else:
        ctx.obj = Configuration.load()


cli.add_command(release)
cli.add_command(repo)
