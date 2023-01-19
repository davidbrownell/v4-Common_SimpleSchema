# ----------------------------------------------------------------------
# |
# |  Integer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:00:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IntegerConstraint and IntegerType objects"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Type as TypeOf

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType
from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.Enum import EnumConstraint


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IntegerConstraint(Constraint):
    """Ensure that a value is a integer value"""

    # ----------------------------------------------------------------------
    # |  Public Types
    class BitsEnum(str, Enum):
        Value8                              = "8 bits"
        Value16                             = "16 bits"
        Value32                             = "32 bits"
        Value64                             = "64 bits"
        Value128                            = "128 bits"

    # ----------------------------------------------------------------------
    # |  Public Data
    min: Optional[int]                                  = field(default=None)
    max: Optional[int]                                  = field(default=None)
    bits: Optional[BitsEnum]                            = field(default=None)

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (int, ))

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        super(IntegerConstraint, self).__post_init__()

        if self.min is not None and self.max is not None and self.min > self.max:
            raise Exception("{} > {}".format(self.min, self.max))

        if self.bits is not None:
            EnumConstraint.Create(IntegerConstraint.BitsEnum)(self.bits)

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
class IntegerType(FundamentalType):
    """An integer"""

    # ----------------------------------------------------------------------
    NAME                                    = "Integer"
    CONSTRAINT_TYPE                         = IntegerConstraint
    EXPRESSION_TYPES                        = IntegerExpression
