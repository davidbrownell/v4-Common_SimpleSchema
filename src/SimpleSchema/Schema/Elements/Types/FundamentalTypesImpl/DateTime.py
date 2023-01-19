# ----------------------------------------------------------------------
# |
# |  DateTime.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:36:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DateTimeConstraint and DateTimeType objects"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple, Type as TypeOf

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
class DateTimeConstraint(Constraint):
    """Ensure that a value is a datetime value"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (datetime, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DateTimeType(FundamentalType):
    """A datetime"""

    # ----------------------------------------------------------------------
    NAME                                    = "DateTime"
    CONTRAINT_TYPE                          = DateTimeConstraint
    EXPRESSION_TYPES                        = None
