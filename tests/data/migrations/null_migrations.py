# -*- coding: utf-8 -*-
from __future__ import absolute_import

from construct.migrations import Migration


class M1(Migration):
    '''Set schema_version to 0.1.1'''

    schema_type = 'test'
    schema_version = (0, 1, 1)

    def forward(self):
        self.entity['schema_version'] = '0.1.1'
        return self.entity

    def backward(self):
        self.entity['schema_version'] = '0.1.1'
        return self.entity

class M2(Migration):

    schema_type = 'test'
    schema_version = (0, 0, 1)

    def forward(self):
        self.entity['schema_version'] = '0.0.1'
        return self.entity

    def backward(self):
        self.entity['schema_version'] = '0.0.1'
        return self.entity


class M3(Migration):

    schema_type = 'test'
    schema_version = (0, 2, 1)

    def forward(self):
        self.entity['schema_version'] = '0.2.1'
        return self.entity

    def backward(self):
        self.entity['schema_version'] = '0.2.1'
        return self.entity


class M4(Migration):

    schema_type = 'test'
    schema_version = (0, 1, 12)

    def forward(self):
        self.entity['schema_version'] = '0.1.12'
        return self.entity

    def backward(self):
        self.entity['schema_version'] = '0.1.12'
        return self.entity


class M5(Migration):

    schema_type = 'test'
    schema_version = (1, 0, 1)

    def forward(self):
        self.entity['schema_version'] = '1.0.1'
        return self.entity

    def backward(self):
        self.entity['schema_version'] = '1.0.1'
        return self.entity
