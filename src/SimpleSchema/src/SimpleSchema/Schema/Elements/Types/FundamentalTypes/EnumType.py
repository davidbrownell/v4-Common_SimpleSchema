# ----------------------------------------------------------------------
# |
# |  EnumType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 16:55:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the EnumType object"""

import itertools

from dataclasses import dataclass, field, InitVar
from enum import Enum, EnumMeta
from typing import Callable, cast, ClassVar, Optional, Tuple, Type as PythonType, Union

from Common_Foundation.Types import overridemethod

from ..FundamentalType import FundamentalType

from .....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class EnumType(FundamentalType):
    """An enum value"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Enum"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (Enum, str, int, )

    values: Union[
        list[int],
        list[str],
        list[Tuple[int, str]],
        list[Tuple[str, str]],
    ]

    starting_value: int                                 = 1

    enum_class_param: InitVar[Optional[EnumMeta]]       = None

    EnumClass: EnumMeta                                 = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        enum_class_param: Optional[EnumMeta],
    ):
        if enum_class_param is not None:
            enum_class = enum_class_param
        else:
            if not self.values:
                raise ValueError("Values must be provided.")

            if isinstance(self.values[0], tuple):
                # ----------------------------------------------------------------------
                def GetTupleValue(index) -> Union[int, str]:
                    v = self.values[index]

                    if not isinstance(v, tuple):
                        raise ValueError("A tuple was expected (index: {}).".format(index))

                    if not v[1]:
                        raise ValueError("A string value is required.")

                    return v[0]

                # ----------------------------------------------------------------------
                def CreateTupleEnumType(
                    value_to_enum_func: Callable[[Union[int, str]], str],
                ) -> EnumMeta:
                    return Enum(
                        "EnumClass",
                        {
                            value_to_enum_func(value[0]): value[1]
                            for value in cast(list[Tuple[Union[int, str], str]], self.values)
                        },
                        type=str,
                    )

                # ----------------------------------------------------------------------

                get_value_func = GetTupleValue
                create_enum_type_func = CreateTupleEnumType

            else:
                # ----------------------------------------------------------------------
                def GetNonTupleValue(index) -> Union[int, str]:
                    v = self.values[index]

                    if isinstance(v, tuple):
                        raise ValueError("A tuple was not expected (index: {}).".format(index))

                    return v

                # ----------------------------------------------------------------------
                def CreateNonTupleEnumType(
                    value_to_enum_name_func: Callable[[Union[int, str]], str],
                ) -> EnumMeta:
                    return Enum(
                        "EnumClass",
                        {
                            value_to_enum_name_func(value): int_value
                            for value, int_value in zip(
                                cast(list[Union[int, str]], self.values),
                                itertools.count(self.starting_value),
                            )
                        },
                    )

                # ----------------------------------------------------------------------

                get_value_func = GetNonTupleValue
                create_enum_type_func = CreateNonTupleEnumType

            if isinstance(get_value_func(0), int):
                value_to_enum_name_func = "Value{}".format

                expected_type = int
                expected_desc = "An Integer"

            elif isinstance(get_value_func(0), str):
                value_to_enum_name_func = lambda value: value

                expected_type = str
                expected_desc = "A String"

            else:
                raise ValueError("An Integer or String value was expected.")

            for value_index in range(1, len(self.values)):
                if not isinstance(get_value_func(value_index), expected_type):
                    raise ValueError("{} was expected (index: {}).".format(expected_desc, value_index))

            enum_class = create_enum_type_func(value_to_enum_name_func)

        # Commit
        object.__setattr__(self, "EnumClass", enum_class)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: Union[Enum, str, int],
    ) -> EnumMeta:
        if isinstance(value, Enum) and value in self.EnumClass:
            return value                    # type: ignore

        if isinstance(value, int):
            # Check by value
            for enum in self.EnumClass:     # type: ignore
                if enum.value == value:     # type: ignore
                    return enum             # type: ignore

            value = "Value{}".format(value)

        if isinstance(value, str):
            # Check by name
            for enum in self.EnumClass:     # type: ignore
                if enum.name == value:      # type: ignore
                    return enum             # type: ignore

            # Check by value
            for enum in self.EnumClass:     # type: ignore
                if enum.value == value:     # type: ignore
                    return enum             # type: ignore

        raise Exception(Errors.enum_type_invalid_value.format(value=value))
