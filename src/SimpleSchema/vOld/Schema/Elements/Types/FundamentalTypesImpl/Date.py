# ----------------------------------------------------------------------
# |
# |  Date.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:40:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DateConstraint and DateType objects"""

from dataclasses import dataclass, field
from datetime import date
from typing import Tuple, Type as TypeOf

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DateConstraint(Constraint):
    """Ensure that a value is a date value"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (date, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DateType(FundamentalType):
    """A date"""

    # ----------------------------------------------------------------------
    NAME                                    = "Date"
    CONSTRAINT_TYPE                         = DateConstraint
    EXPRESSION_TYPES                        = None
