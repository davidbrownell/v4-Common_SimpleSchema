# ----------------------------------------------------------------------
# |
# |  Number.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:09:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NumberConstraint and NumberType objects"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Type as TypeOf

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType
from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.Enum import EnumConstraint


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NumberConstraint(Constraint):
    """Ensure that a value is a number value"""

    # ----------------------------------------------------------------------
    # |  Public Types
    class BitsEnum(str, Enum):
        Value16                             = "IEEE 754 half precision"
        Value32                             = "IEEE 754 single precision"
        Value64                             = "IEEE 754 double precision"
        Value128                            = "IEEE 754 quadruple precision"
        Value256                            = "IEEE 754 octuple precision"

    # ----------------------------------------------------------------------
    # |  Public Data
    min: Optional[float]                                = field(default=None)
    max: Optional[float]                                = field(default=None)
    bits: Optional[BitsEnum]                            = field(default=None)

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (float, int))

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        super(NumberConstraint, self).__post_init__()

        if self.min is not None and self.max is not None and self.min > self.max:
            raise Exception("{} > {}".format(self.min, self.max))

        if self.bits is not None:
            EnumConstraint.Create(NumberConstraint.BitsEnum)(self.bits)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ValidateImpl(
        self,
        value: int,
    ) -> int:
        if self.min is not None and value < self.min:
            raise Exception("{} < {}".format(value, self.min))

        if self.max is not None and value > self.max:
            raise Exception("{} > {}".format(value, self.max))

        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NumberType(FundamentalType):
    """A number"""

    # ----------------------------------------------------------------------
    NAME                                    = "Number"
    CONSTRAINT_TYPE                         = NumberConstraint
    EXPRESSION_TYPES                        = (NumberExpression, IntegerExpression)
