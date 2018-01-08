# -*- coding: utf-8 -*-
__all__ = [
    'Priority',
    'STAGE0',
    'STAGE1',
    'STAGE2',
    'STAGE3',
    'STAGE4',
    'COLLECT',
    'VALIDATE',
    'REPAIR',
    'CREATE',
]


class Priority(int):

    _instances = {}

    def __new__(cls, value, label=None, description=None):

        key = (value, label, description)
        if key in cls._instances:
            return cls._instances[key]

        if label is None:
            label = 'Priority-' + str(value)

        if description is None:
            description = 'Priority ' + str(value)

        key = (value, label, description)
        if key in cls._instances:
            return cls._instances[key]

        obj = super(Priority, cls).__new__(cls, value)
        obj.label = label
        obj.description = description

        return cls._instances.setdefault(key, obj)


STAGE0 = Priority(0, 'Stage-0', 'First stage')
STAGE1 = Priority(1, 'Stage-1', 'Second stage')
STAGE2 = Priority(2, 'Stage-2', 'Third stage')
STAGE3 = Priority(3, 'Stage-3', 'Fourth stage')
STAGE4 = Priority(4, 'Stage-4', 'Fifth stage')

COLLECT = Priority(0, 'Collect', 'Collect data for validation')
VALIDATE = Priority(1, 'Validate', 'Validate collected data')
REPAIR = Priority(2, 'Repair', 'Repair data that failed validation')
CREATE = Priority(3, 'Create', 'Create new artifacts based on collected data')

DEFAULTS = {
    (0, None, None): STAGE0,
    (1, None, None): STAGE1,
    (2, None, None): STAGE2,
    (3, None, None): STAGE3,
    (4, None, None): STAGE4,
}
Priority._instances.update(DEFAULTS)
