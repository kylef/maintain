Repo
====

Commands to operate on a collection of repositories at a time.

print
-----

Subcommand to print all matched repositories, this is useful to test which repositories will be used for other operations.

check
-----

Checks all repositories for unstaged, unsynced or untracked changes.

.. code-block::

    $ maintain repo check
    goji
     - Branch is not master
     - Repository has unstaged changes

run
---

Allows running the provided command on a collection of repositories.

.. code-block::

    $ maintain repo run 'npm install && npm test'

Options

-s/--silent - Don't print subcommand output
--exit - Exit after first failure (non zero exit)
