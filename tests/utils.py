import os
import tempfile
import shutil


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
        os.makedirs(path)

    with open(filename, 'w') as fp:
        fp.write(contents)
