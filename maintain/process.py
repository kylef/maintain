import os
import subprocess
import tempfile
import shutil
import click


def invoke(command, error_message=None):
    status = subprocess.call(command)

    if status != 0:
        if error_message is None:
            error_message = 'Command failed: {}'.format(' '.join(command))

        click.echo(error_message)
        exit(1)


class chdir(object):
    def __init__(self, directory):
        self.directory = directory

    def __enter__(self):
        self.working_directory = os.getcwd()
        os.chdir(self.directory)
        return self.directory

    def __exit__(self, typ, value, traceback):
        os.chdir(self.working_directory)


class temp_directory(object):
    def __enter__(self):
        self.working_directory = os.getcwd()
        self.pathname = tempfile.mkdtemp()
        os.chdir(self.pathname)
        return self.pathname

    def __exit__(self, typ, value, traceback):
        os.chdir(self.working_directory)
        shutil.rmtree(self.pathname)
