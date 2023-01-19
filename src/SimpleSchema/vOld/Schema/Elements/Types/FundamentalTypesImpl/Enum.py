# ----------------------------------------------------------------------
# |
# |  Enum.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:48:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the EnumConstraint and EnumType objects"""

import itertools

from dataclasses import dataclass, field, InitVar
from enum import Enum, EnumMeta
from typing import Callable, cast, List, Tuple, Type as TypeOf, Union

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType
from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.String import StringConstraint


# ----------------------------------------------------------------------
class EnumConstraint(Constraint):
    """Ensure that a value is a boolean value"""

    values: InitVar[
        Union[
            list[int],
            list[str],
            list[Tuple[int, str]],
            list[Tuple[str, str]],
            EnumMeta,
        ]
    ]

    starting_value: InitVar[int]                        = field(default=0)

    EnumClass: EnumMeta                                 = field(init=False)

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (int, str, EnumMeta))

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        values: Union[
            list[int],
            list[str],
            list[Tuple[int, str]],
            list[Tuple[str, str]],
        ],
        starting_value: int,
    ):
        super(EnumConstraint, self).__post_init__()

        if not values:
            raise Exception("Values must be provided.")

        if isinstance(values, EnumMeta):
            enum_class = values
        else:
            non_empty_string_constraint = StringConstraint.Create()

            if isinstance(values[0], tuple):
                # ----------------------------------------------------------------------
                def GetTupleValue(index) -> Union[int, str]:
                    v = values[index]

                    if not isinstance(v, tuple):
                        raise Exception("A tuple was expected (index: {}).".format(index))

                    non_empty_string_constraint(v[1])

                    return v[0]

                # ----------------------------------------------------------------------
                def CreateTupleEnumType(
                    value_to_enum_name_func: Callable[[Union[int, str]], str],
                ) -> EnumMeta:
                    enum_values = {
                        value_to_enum_name_func(value[0]): value[1]
                        for value in cast(List[Tuple[Union[int, str], str]], values)
                    }

                    return Enum(
                        "EnumClass",
                        enum_values,
                        type=str,
                    )

                # ----------------------------------------------------------------------

                get_value_func = GetTupleValue
                create_enum_type_func = CreateTupleEnumType

            else:
                # ----------------------------------------------------------------------
                def GetNonTupleValue(index) -> Union[int, str]:
                    v = values[index]

                    if isinstance(v, tuple):
                        raise Exception("A tuple was not expected (index: {}).".format(index))

                    return v

                # ----------------------------------------------------------------------
                def CreateNonTupleEnumType(
                    value_to_enum_name_func: Callable[[Union[int, str]], str],
                ) -> EnumMeta:
                    return Enum(
                        "EnumClass",
                        {
                            value_to_enum_name_func(value): int_value
                            for value, int_value in zip(cast(List[Union[int, str]], values), itertools.count(starting_value))
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
                value_to_enum_name_func = non_empty_string_constraint

                expected_type = str
                expected_desc = "A String"

            else:
                raise Exception("An Integer or String value was expected.")

            for value_index in range(len(values)):
                if not isinstance(get_value_func(value_index), expected_type):
                    raise Exception("{} was expected (index: {}).".format(expected_desc, value_index))

            enum_class = create_enum_type_func(value_to_enum_name_func)

        # Commit
        object.__setattr__(self, "EnumClass", enum_class)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ValidateImpl(
        self,
        value: Union[int, str, EnumMeta],
    ) -> EnumMeta:
        if isinstance(value, EnumMeta) and value in self.EnumClass:  # pylint: disable=unsupported-membership-test
            return value

        if isinstance(value, int):
            value = "Value{}".format(value)

        if isinstance(value, str):
            # Check by name
            for enum in self.EnumClass:     # type: ignore  # pylint: disable=not-an-iterable
                if enum.name == value:      # type: ignore
                    return enum             # type: ignore

            # Check by value
            for enum in self.EnumClass:     # type: ignore  # pylint: disable=not-an-iterable
                if enum.value == value:     # type: ignore
                    return enum             # type: ignore

        raise Exception("'{}' is not a valid enum value.".format(value))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class EnumType(FundamentalType):
    """An enum"""

    # ----------------------------------------------------------------------
    NAME                                    = "Enum"
    CONSTRAINT_TYPE                         = EnumConstraint
    EXPRESSION_TYPES                        = (IntegerExpression, StringExpression)
