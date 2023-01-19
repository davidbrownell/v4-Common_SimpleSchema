# ----------------------------------------------------------------------
# |
# |  String.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:11:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StringConstraint and StringType objects"""

import re

from dataclasses import dataclass, field, InitVar
from typing import Optional, Pattern, Tuple, Type as TypeOf

from Common_Foundation.Types import overridemethod
from Common_FoundationEx.InflectEx import inflect

from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StringConstraint(Constraint):
    """Ensure that a value is a string value"""

    # ----------------------------------------------------------------------
    min_length: int                                     = field(default=1)
    max_length: Optional[int]                           = field(default=None)

    validation_expression: InitVar[Optional[str]]       = field(default=None)
    validation_regex: Optional[Pattern]                 = field(init=False)

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (str, ))

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        validation_expression: Optional[str],
    ):
        super(StringConstraint, self).__post_init__()

        # Importing here to break a circular import between Enum -> String -> Integer
        from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.Integer import IntegerConstraint

        positive_integer_constraint = IntegerConstraint(1)

        positive_integer_constraint(self.min_length)

        if self.max_length is not None:
            positive_integer_constraint(self.max_length)

            if self.min_length > self.max_length:
                raise Exception("{} > {}".format(self.min_length, self.max_length))

        if validation_expression is None:
            regex = None
        else:
            regex = re.compile(validation_expression)

        object.__setattr__(self, "validation_regex", regex)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ValidateImpl(
        self,
        value: str,
    ) -> str:
        num_chars = len(value)

        if num_chars < self.min_length:
            raise Exception(
                "At least {} {} expected ({} {} found).".format(
                    inflect.no("characters", self.min_length),
                    inflect.plural_verb("was", self.min_length),
                    inflect.no("characters", num_chars),
                    inflect.plural_verb("was", num_chars),
                ),
            )

        if self.max_length is not None and num_chars > self.max_length:
            raise Exception(
                "Only {} {} expected ({} {} found).".format(
                    inflect.no("characters", self.max_length),
                    inflect.plural_verb("was", self.max_length),
                    inflect.no("characters", num_chars),
                    inflect.plural_verb("was", num_chars),
                ),
            )

        if self.validation_regex is not None and not self.validation_regex.match(value):
            raise Exception(
                "The string '{}' did not match the regular expression '{}'.".format(
                    value,
                    self.validation_regex.pattern,
                ),
            )

        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StringType(FundamentalType):
    """A string"""

    # ----------------------------------------------------------------------
    NAME                                    = "String"
    CONSTRAINT_TYPE                         = StringConstraint
    EXPRESSION_TYPES                        = StringExpression
