Maintain
========

A unified interface to maintaining projects of any language.

Installation
------------

.. code-block:: shell

    $ pip install maintain

Release Automation
------------------

Maintain offers a command to automate bumping version numbers and releasing
your project.

.. code-block:: shell

    $ maintain release patch

This release command will figured out the type of package, whether it be a
Python package, Ruby Gem, NPM package etc and then perform the steps necessary
to release it. It will bump the version number, create a release commit, tag
the release and push it to the respective package manager.

Maintain allows you to specify the `major`, `minor` or `patch` to automatically
bump the respective version number, or you can explicitly specify a version.

You may also specify `semver` as the version to automatically determine the
next semantic version. This is not supported on all releasers.

Pull-request
~~~~~~~~~~~~

You can configure Maintain to create a pull request and perform the release in
two steps. This is useful if you use code-review for the release process:

.. code-block:: shell

    $ maintain release 1.2.0-beta.1 --pull-request

Once the pull request is merged, you can perform the actual release:

.. code-block:: shell

    $ maintain release --no-bump

.. note:: This step could be done during continuous integration.

Releasers
~~~~~~~~~

Maintain supports the following releasers:

.. toctree::
   :maxdepth: 1

   repo
   release/hooks
   release/git
   release/github
   release/version-file
   release/changelog
   release/python
   release/rubygems
   release/npm
   release/cocoapods
   release/c

Custom Hooks
~~~~~~~~~~~~

By creating a `.maintain.yml` file in the root of your repository, you can add
hooks to various stages of the release process.

.. code-block:: yaml

    release:
      bump:
        pre:
        - echo 'Hook ran before the version is bumped'
        post:
        - echo 'Hook ran after the version is bumped'
      publish:
        pre:
        - echo 'Hook ran before the library is published'
        post:
        - echo 'Hook ran after the library is published'
