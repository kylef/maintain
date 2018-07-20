Repo
====

Commands to operate on a collection of repositories at a time.

print
-----

Subcommand to print all matched repositories, this is useful to test which repositories will be used for other operations.

run
---

Allows running the provided command on a collection of repositories.

.. code-block::

    $ maintain repo run 'npm install && npm test'

Options

-s/--silent - Don't print subcommand output
--exit - Exit after first failure (non zero exit)
