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

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Tuple, Type as TypeOf, Union, cast
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class EnumType(FundamentalType):
    NAME = "Enum"

    # ----------------------------------------------------------------------
    _EnumItemType = Union[int, str]

    values: Union[
        List[_EnumItemType],
        List[Tuple[_EnumItemType, str]],
    ]

    starting_value: int                 = field(default=0)

    EnumClass: TypeOf[Enum]             = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(EnumType, self).__post_init__()

        if not self.values:
            raise SimpleSchemaException("Enum values must be provided.", self.range)

        if self.starting_value < 0:
            raise SimpleSchemaException("'starting_value' must be greater than or equal to '0' ('{}' was provided).".format(self.starting_value), self.range)

        if isinstance(self.values[0], tuple):
            # ----------------------------------------------------------------------
            def GetTupleValue(index):
                v = self.values[index]

                if not isinstance(v, tuple):
                    raise SimpleSchemaException("A tuple was expected (index: {}).".format(index), self.range)

                return v[0]

            # ----------------------------------------------------------------------
            def CreateTupleEnumType(
                value_to_enum_name_func: Callable[[EnumType._EnumItemType], str],
            ) -> TypeOf[Enum]:
                return Enum(
                    "EnumClass",
                    {
                        value_to_enum_name_func(value[0]): value[1]
                        for value in cast(List[Tuple[EnumType._EnumItemType, str]], self.values)
                    },
                    type="str",
                )

            # ----------------------------------------------------------------------

            get_value_func = GetTupleValue
            create_enum_type = CreateTupleEnumType

        else:
            # ----------------------------------------------------------------------
            def GetNonTupleValue(index):
                v = self.values[index]

                if isinstance(v, tuple):
                    raise SimpleSchemaException("A tuple value was not expected (index: {}).".format(index), self.range)

                return v

            # ----------------------------------------------------------------------
            def CreateNonTupleEnumType(
                value_to_enum_name_func: Callable[[EnumType._EnumItemType], str],
            ) -> TypeOf[Enum]:
                import itertools

                return Enum(
                    "EnumClass",
                    {
                        value_to_enum_name_func(value): int_value
                        for value, int_value in zip(cast(List[EnumType._EnumItemType], self.values), itertools.count(self.starting_value))
                    },
                )

            # ----------------------------------------------------------------------

            get_value_func = GetNonTupleValue
            create_enum_type = CreateNonTupleEnumType

        if isinstance(get_value_func(0), int):
            value_to_enum_name_func = lambda value: "Value{}".format(value)  # pylint: disable=unnecessary-lambda

            for value_index in range(len(self.values)):
                if not isinstance(get_value_func(value_index), int):
                    raise SimpleSchemaException("An integer was expected (index: {}).".format(value_index), self.range)

        elif isinstance(get_value_func(0), str):
            value_to_enum_name_func = lambda value: value

            for value_index in range(len(self.values)):
                if not isinstance(get_value_func(value_index), str):
                    raise SimpleSchemaException("A string was expected (index: {}).".format(value_index), self.range)

        else:
            raise SimpleSchemaException("A string or integer is required.", self.range)

        object.__setattr__(self, "EnumClass", create_enum_type(value_to_enum_name_func))
