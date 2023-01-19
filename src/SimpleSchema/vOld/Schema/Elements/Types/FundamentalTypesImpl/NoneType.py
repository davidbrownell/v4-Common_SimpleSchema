# ----------------------------------------------------------------------
# |
# |  NoneType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:05:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneConstraint and NoneType objects"""

from dataclasses import dataclass, field
from types import NoneType as PythonNoneType
from typing import Tuple, Type as TypeOf

from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneConstraint(Constraint):
    """Ensure that a value is None"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (PythonNoneType, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneType(FundamentalType):
    """A None value"""

    # ----------------------------------------------------------------------
    NAME                                    = "None"
    CONSTRAINT_TYPE                         = NoneConstraint
    EXPRESSION_TYPES                        = NoneExpression
