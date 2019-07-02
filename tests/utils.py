import os
import sys
import tempfile
import shutil

from git import Repo


if sys.version_info.major == 2:
    FileExistsError = OSError


class temp_directory(object):
    def __enter__(self):
        self.working_directory = os.getcwd()
        self.pathname = tempfile.mkdtemp()
        os.chdir(self.pathname)
        return self.pathname

    def __exit__(self, typ, value, traceback):
        os.chdir(self.working_directory)
        shutil.rmtree(self.pathname)


def touch(filename, contents=''):
    path, _ = os.path.split(filename)
    if len(path) > 0:
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

    with open(filename, 'w') as fp:
        fp.write(contents)


class git_bare_repo(temp_directory):
    def __enter__(self):
        path = super(git_bare_repo, self).__enter__()
        Repo.init(bare=True)
        return path


class git_repo(temp_directory):
    def __enter__(self):
        super(git_repo, self).__enter__()
        return Repo.init()
