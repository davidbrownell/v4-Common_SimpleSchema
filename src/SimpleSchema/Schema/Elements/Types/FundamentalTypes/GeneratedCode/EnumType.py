# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
#
# The file has been automatically generated via ../Build.py using content
# in ../SimpleSchema.
#
# DO NOT MODIFY the contents of this file, as those changes will be
# overwritten the next time ../Build.py is invoked.
#
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

from dataclasses import dataclass
from typing import List, Tuple, Union
from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class EnumType(Type):
    _EnumItemType = Union[int, str]

    values: Union[
        List[_EnumItemType],
        List[Tuple[_EnumItemType, str]],
    ]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.values:
            raise SimpleSchemaException("Enum values must be provided.", self.range)

        if isinstance(self.values[0], tuple):
            get_value_func = lambda v: v[0]
        else:
            get_value_func = lambda v: v

        if isinstance(get_value_func(self.values[0]), int):
            for value_index, value in enumerate(self.values):
                if not isinstance(get_value_func(value), int):
                    raise SimpleSchemaException("An integer was expected (index: {}).".format(value_index), self.range)

        elif isinstance(get_value_func(self.values[0]), str):
            for value_index, value in enumerate(self.values):
                if not isinstance(get_value_func(value), str):
                    raise SimpleSchemaException("A string was expected (index: {}).".format(value_index), self.range)

        else:
            assert False, get_value_func(self.values[0])  # pragma: no cover
