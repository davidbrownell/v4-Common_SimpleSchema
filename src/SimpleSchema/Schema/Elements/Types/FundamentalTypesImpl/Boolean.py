# ----------------------------------------------------------------------
# |
# |  BooleanType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:30:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BooleanConstraint and BooleanType objects"""

from dataclasses import dataclass, field
from typing import Tuple, Type as TypeOf

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BooleanConstraint(Constraint):
    """Ensure that a value is a boolean value"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (bool, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BooleanType(FundamentalType):
    """A Boolean"""

    # ----------------------------------------------------------------------
    NAME                                    = "Boolean"
    CONSTRAINT_TYPE                         = BooleanConstraint
    EXPRESSION_TYPES                        = BooleanExpression