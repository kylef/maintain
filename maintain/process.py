import os
import shutil
import subprocess
import tempfile

import click


def invoke(command, error_message=None) -> None:
    status = subprocess.call(command)

    if status != 0:
        if error_message is None:
            error_message = "Command failed: {}".format(" ".join(command))

        click.echo(error_message)
        exit(1)


class chdir(object):
    def __init__(self, directory: str):
        self.directory = directory

    def __enter__(self) -> str:
        self.working_directory = os.getcwd()
        os.chdir(self.directory)
        return self.directory

    def __exit__(self, typ, value, traceback):
        os.chdir(self.working_directory)
