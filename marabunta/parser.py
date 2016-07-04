# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function


import yaml

from .exception import ParseError
from .model import Migration, MigrationOption, Version, Operation

YAML_EXAMPLE = u"""
name: project_name
migration:
  options:
    # --workers=0 --stop-after-init are automatically added
    install_command: odoo.py
    install_args: --log-level=debug
  versions:
    - version: 0.0.1
      operations:
        base:
          pre:  # executed before 'addons'
            - echo 'pre-operation'
          post:  # executed after 'addons'
            - anthem songs::install
        prod:
          pre:
            - echo 'pre-operation executed only when the mode is prod'
          post:
            - anthem songs::load_production_data
        demo:
          post:
            - anthem songs::load_demo_data
      addons:
        upgrade:  # executed as odoo.py --stop-after-init -i/-u ...
          - base
          - document
        # remove:  # uninstalled with a python script

    - version: 0.0.2
      # nothing to do

    - version: 0.0.3
      operations:
        base:
          pre:
            - echo 'foobar'
            - ls
            - bin/script_test.sh
          post:
            - echo 'post-op'

    - version: 0.0.4
      addons:
        upgrade:
          - popeye

"""


class YamlParser(object):

    def __init__(self, parsed):
        self.parsed = parsed

    @classmethod
    def parser_from_buffer(cls, fp):
        """Construct YamlParser from a file pointer."""
        return cls(yaml.safe_load(fp))

    @classmethod
    def parse_from_file(cls, filename):
        """Construct YamlParser from a filename."""
        with open(filename, 'rU') as fh:
            return cls.parser_from_buffer(fh)

    def check_dict_expected_keys(self, expected_keys, current, dict_name):
        """ Check that we don't have unknown keys in a dictionary.

        It does not raise an error if we have less keys than expected.
        """
        if not isinstance(current, dict):
            raise ParseError("'{}' key must be a dict".format(dict_name),
                             YAML_EXAMPLE)
        expected_keys = set(expected_keys)
        current_keys = {key for key in current}
        extra_keys = current_keys - expected_keys
        if extra_keys:
            message = "{}: the keys {} are unexpected. (allowed keys: {})"
            raise ParseError(
               message.format(dict_name,
                              list(extra_keys),
                              list(expected_keys)),
               YAML_EXAMPLE
            )

    def parse(self):
        """Check input and return a :class:`Migration` instance."""
        if not self.parsed.get('migration'):
            raise ParseError("'migration' key is missing", YAML_EXAMPLE)
        self.check_dict_expected_keys(
            {'options', 'versions'}, self.parsed['migration'], 'migration',
        )
        return self._parse_migrations()

    def _parse_migrations(self):
        """Build a :class:`Migration` instance."""
        migration = self.parsed['migration']
        options = self._parse_options(migration)
        versions = self._parse_versions(migration, options)
        return Migration(versions)

    def _parse_options(self, migration):
        options = migration.get('options') or {}
        install_command = options.get('install_command')
        install_args = options.get('install_args') or ''
        return MigrationOption(install_command=install_command,
                               install_args=install_args.split())

    def _parse_versions(self, migration, options):
        versions = migration.get('versions') or []
        if not isinstance(versions, list):
            raise ParseError("'versions' key must be a list", YAML_EXAMPLE)
        return [self._parse_version(version, options) for version in versions]

    def _parse_version(self, parsed_version, options):
        number = parsed_version.get('version')
        if not number:
            raise ParseError("'version' key with the number is mandatory",
                             YAML_EXAMPLE)
        version = Version(number, options)

        operations = parsed_version.get('operations') or {}
        for operation_mode, operation_types in operations.items():
            self.check_dict_expected_keys(
                {'pre', 'post'}, operation_types, operation_mode,
            )
            for operation_type, commands in operation_types.items():
                if not isinstance(commands, list):
                    raise ParseError("'%s' key must be a list" %
                                     (operation_type,), YAML_EXAMPLE)
                for command in commands:
                    version.add_operation(
                        operation_mode,
                        operation_type,
                        Operation(command)
                    )

        addons = parsed_version.get('addons') or {}
        self.check_dict_expected_keys(
            {'upgrade', 'remove'}, addons, 'addons',
        )
        upgrade = addons.get('upgrade') or []
        if upgrade:
            if not isinstance(upgrade, list):
                raise ParseError("'upgrade' key must be a list", YAML_EXAMPLE)
            version.add_upgrade_addons(upgrade)
        remove = addons.get('remove') or []
        if remove:
            if not isinstance(remove, list):
                raise ParseError("'remove' key must be a list", YAML_EXAMPLE)
            version.add_remove_addons(remove)
        return version
