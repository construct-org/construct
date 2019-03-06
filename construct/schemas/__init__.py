# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import getpass
import datetime

import yaml
import json
from cachetools import cached
from cerberus import Validator, schema_registry
from cerberus.schema import SchemaRegistry
from bson.objectid import ObjectId
from builtins import open, bytes


schemas_root = os.path.abspath(os.path.dirname(__file__))


class SchemaNotFound(Exception): pass


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
        return yaml.safe_dump(self.errors, default_flow_style=False)

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

    potential_path = os.path.join(schemas_root, name + '.yaml')
    if not os.path.isfile(potential_path):
        raise SchemaNotFound('Could not find a schema named %s' % name)

    with open(potential_path, 'rb') as f:
        schema_text = f.read().decode('utf-8')

    return yaml.load(schema_text)


def ls(subdir=None):
    '''Yields schemas from the schemas_root or a specified subdir.

    Returns:
        generator yielding (schema_name, schema_dict) pairs
    '''

    if subdir:
        root = os.path.join(schemas_root, subdir)
    else:
        root = schemas_root

    for f in os.listdir(root):
        if f.endswith('.yaml'):
            schema_name = f[:-5]
            if subdir:
                schema_name = subdir + '/' + schema_name
            yield schema_name, get_schema(schema_name)


_schema_registry = SchemaRegistry()
for schema_name, schema in ls():
    _schema_registry.add(schema_name, schema)
