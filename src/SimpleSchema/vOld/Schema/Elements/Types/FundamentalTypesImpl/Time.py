# ----------------------------------------------------------------------
# |
# |  Time.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:19:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TimeConstraint and TimeType objects"""

from dataclasses import dataclass, field
from datetime import time
from typing import Tuple, Type as TypeOf

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TimeConstraint(Constraint):
    """Ensure that a value is a time value"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (time, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TimeType(FundamentalType):
    """A time"""

    # ----------------------------------------------------------------------
    NAME                                    = "Time"
    CONSTRAINT_TYPE                         = TimeConstraint
    EXPRESSION_TYPES                        = None
