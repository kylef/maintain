import subprocess
import click


def invoke(command, error_message=None):
    status = subprocess.call(command)

    if status != 0:
        if error_message is None:
            error_message = 'Command failed: {}'.format(' '.join(command))

        click.echo(error_message)
        exit(1)

