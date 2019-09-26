# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard library imports
import datetime
import getpass
import json
import os

# Third party imports
from bson.objectid import ObjectId
from cachetools import cached
from cerberus import Validator
from cerberus.schema import SchemaRegistry

# Local imports
from ..compat import Path
from ..errors import ValidationError
from ..utils import yaml_dump, yaml_load


package_path = Path(__file__).parent.resolve()


class SchemaNotFound(Exception): pass
class SchemaError(Exception): pass


class ConstructValidator(Validator):

    def _validate_type_objectid(self, value):
        return ObjectId.is_valid(value)

    def _normalize_default_setter_objectid(self, document):
        return str(ObjectId())

    def _normalize_default_setter_utcnow(self, document):
        return datetime.datetime.utcnow()

    def _normalize_default_setter_getuser(self, document):
        return getpass.getuser()

    def _normalize_default_setter_empty_string(self, document):
        return ''

    def _normalize_default_setter_empty_list(self, document):
        return []

    def _normalize_default_setter_empty_dict(self, document):
        return {}

    @property
    def errors_yaml(self):
        return yaml_dump(self.errors)

    @property
    def errors_json(self):
        return json.dumps(self.errors)


@cached(cache={})
def get_validator(schema_name, **kwargs):
    '''Get a validator for one of Constructs builtin schemas.

    Examples:
        new_project = {...}
        v = get_validator('project')
        if v.validate(new_project):
            new_project = v.normalized(new_project)
    '''
    return new_validator(get_schema(schema_name), **kwargs)


def new_validator(schema, **kwargs):
    kwargs.setdefault('schema_registry', _schema_registry)
    return ConstructValidator(schema, **kwargs)


@cached(cache={})
def get_schema(name):
    '''Get a Cerberus schema dict by name.'''

    schema_file = package_path / (name + '.yaml')
    if not schema_file.is_file():
        raise SchemaNotFound('Could not find a schema named %s' % name)

    return yaml_load(schema_file.read_text(encoding='utf-8'))


def validate(schema_name, data, **kwargs):
    kwargs.setdefault('allow_unknown', True)
    v = get_validator(schema_name, **kwargs)
    data = v.validated(data)
    if not data:
        raise ValidationError(
            'Data does not match "%s" schema.\n%s'
            % (schema_name, v.errors_yaml),
            errors=v.errors
        )
    return data


def ls(subdir=None):
    '''Yields schemas from the schemas_root or a specified subdir.

    Returns:
        generator yielding (schema_name, schema_dict) pairs
    '''

    if subdir:
        root = package_path / subdir
    else:
        root = package_path

    for schema_file in root.glob('*.yaml'):
        schema_name = schema_file.stem
        if subdir:
            schema_name = subdir + '/' + schema_name
        yield schema_name, get_schema(schema_name)


_schema_registry = SchemaRegistry()
for schema_name, schema in ls():
    _schema_registry.add(schema_name, schema)
