🐜🐜🐜 Marabunta 🐜🐜🐜
=======================

.. image:: https://travis-ci.org/camptocamp/marabunta.svg?branch=master
    :target: https://travis-ci.org/camptocamp/marabunta

Marabunta is used to provide an easy way to provide updates to Odoo which can be created fast and run easily. It also allows to differentiate between different environment to provide for instance demodata.


Usage
=====
After installing marabunta will be available as a console command. To run properly it requires a migration file, which defines what should be updated/executed, and of course stuff like database pw. Most of these also can also be provided by an envvar and will be discussed in the options section.

It is very much recomended to configure it, so that marabunta is ran automatically if odoo is started.
For instance adding it to your docker entrypoint.

Features
========

* backup: Marabunta allows for a backup command to be executed before the migration.
* addon upgrades: Marabunta is able to install or upgrade odoo addons.
* addon uninstall: Addons which were previously installed can be removed with marabunta.
* operations: Allows to execute commands before or after upgrading modules.
* modes: Modes allow the user to execute commands only on a certain environment. i.e. creation of demodata on a dev system.

Versioning systems
------------------
Currently Marabunta allows for two different Versioning systems:
The classic Major.Minor.Bugfix and the Five digits long versions for OdooMajor.OdooMinor.Major.Minor.Bugfix.
Although the first marabunta version should always be called setup. This is a standin for all the versions till the release, to make it easier to keep marabunta versions and tags in sync.


Options
=======

=================  ========  ========================   ===============================================
option             shortcut  envvar                     purpose
=================  ========  ========================   ===============================================
--migration-file   -f        MARABUNTA_MIGRATION_FILE   Definition file for the migration.
--database         -d        MARABUNTA_DATABASE         Database we want to run the migration on.
--db-user          -u        MARABUNTA_DB_USER          Database user.
--db-password      -w        MARABUNTA_DB_PASSWORD      Database password.
--db-port          -p        MARABUNTA_DB_PORT          Database port (defaults to 5432).
--db-host          -H        MARABUNTA_DB_HOST          Database port (defaults to localhost).
--mode                       MARABUNTA_MODE             Mode marabunta runs in for different envs.
--allow-serie                MARABUNTA_ALLOW_SERIE      Allow multiple versions to be upgraded at once.
--force-version              MARABUNTA_FORCE_VERSION    Force the upgrade to a version no matter what.
--web-host                   MARABUNTA_WEB_HOST         Interface to bind (defaults to 0.0.0.0).
--web-port                   MARABUNTA_WEB_PORT         Port for the Webhost (defaults to 8069).
--web-custom-html            MARABUNTA_WEB_CUSTOM_HTML  Path to custom html page to serve.
=================  ========  =========================  ===============================================

YAML layout & Example
=====================
Here is an Example migration file::
    migration:
      options:
        # This includes general options which are used everytime marabunta is called.
        # --workers=0 --stop-after-init are automatically added
        install_command: odoo #Command which starts odoo
        install_args: --log-level=debug # additional Arguments
        backup: # Defines how the backup should be done before the migration.
          command: echo "backup command on ${DB_NAME}"
          stop_on_failure: true
          ignore_if: test "${RUNNING_ENV}" != "prod"
      versions:
        - version: setup # Setup is always the initia. version<
          operations:
            pre:  # executed before 'addons'
              - echo 'pre-operation'
            post:  # executed after 'addons'
              - anthem songs::install
          addons:
            upgrade:  # executed as odoo --stop-after-init -i/-u ...
              - base
              - document
            # remove:  # uninstalled with a python script
          modes:
            prod:
              operations:
                pre:
                  - echo 'pre-operation executed only when the mode is prod'
                post:
                  - anthem songs::load_production_data
            demo:
              operations:
                post:
                  - anthem songs::load_demo_data
              addons:
                upgrade:
                  - demo_addon

        - version: 0.0.2
          backup: false
          # nothing to do this can be used to keep marabunta and gittag in sync

        - version: 0.0.3
          operations:
            pre: # we also can execute os commands
              - echo 'foobar'
              - ls
              - bin/script_test.sh
            post:
              - echo 'post-op'

        - version: 0.0.4
          backup: false
          addons:
            upgrade:
              - popeye


Run the tests
-------------

To run ``marabunta`` tests, it is a good idea to do an *editable*
install of it in a virtualenv, and then intall and run ``pytest`` as
follows::

  $ git clone https://github.com/camptocamp/marabunta.git
  Cloning into 'marabunta'...
  $ cd marabunta
  $ virtualenv -p YOUR_PYTHON env
  $ source env/bin/activate
  $ pip install '.[test]'
  $ py.test tests
