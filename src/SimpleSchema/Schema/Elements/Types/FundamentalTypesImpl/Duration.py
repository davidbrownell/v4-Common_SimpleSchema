# ----------------------------------------------------------------------
# |
# |  Duration.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:47:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DurationConstraint and DurationType objects"""

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Tuple, Type as TypeOf

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DurationConstraint(Constraint):
    """Ensure that a value is a duration value"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (timedelta, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DurationType(FundamentalType):
    """A duration"""

    # ----------------------------------------------------------------------
    NAME                                    = "Duration"
    CONSTRAINT_TYPE                         = DurationConstraint
    EXPRESSION_TYPES                        = None
