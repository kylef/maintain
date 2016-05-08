# Python Releaser

## Detect

The Python releaser looks for a `setup.py` file in the root of your library.

## Bump

Bumping will update the version qualifier directly in your `setup.py`.

## Release

The release stage of the Python releaser depends on `twine` and `wheel`, which
can be installed via [pip](https://pip.pypa.io/):

```shell
$ pip install twine wheel
```

You will need to register your project with PyPI before you can release, which
can be done via the following:

```shell
$ python setup.py register
```
