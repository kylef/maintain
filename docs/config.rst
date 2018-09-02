Maintain Configuration
======================

Maintain can be configured via a configuration file in your project.

The configuration file (if present) is expected to be in one of the following locations:

* ``.maintain.yaml``
* ``.maintain.yml``
* ``.maintain/config.yaml``
* ``.maintain/config.yml``

The configuration format is YAML and each part of maintain has separate
configuration. For example, to configure releasers you would use a
configuration like the following.

.. code-block:: yaml

    release:
      git:
        tag_format: maintain-{version}

Remote Configuration
--------------------

If you have many projects across your organisation you may wish to adopt a
standardised config that applies to multiple projects.

Using the following syntax you may reference a remote configuration file:

.. code-block:: yaml

    $ref: https://example.com/maintain.yaml

It is strongly recommended that your remote configration files are versoned in
the URL so that upstream changes cannot break downstream projects. You don't
want to discover that an upstream configuration change breaks a downstream
release in your CI/CD pipeline, you want to have full control over updating the
project for compatibility.

.. code-block:: yaml

    $ref: https://github.com/kylef/maintain/raw/1.0.0/.maintain.yaml

