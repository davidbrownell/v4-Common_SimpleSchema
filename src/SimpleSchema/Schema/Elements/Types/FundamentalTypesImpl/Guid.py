# ----------------------------------------------------------------------
# |
# |  Guid.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:58:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GuidConstraint and GuidType objects"""

from dataclasses import dataclass, field
from typing import Tuple, Type as TypeOf
from uuid import UUID

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class GuidConstraint(Constraint):
    """Ensure that a value is a guid value"""

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (UUID, ))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class GuidType(FundamentalType):
    """A guid"""

    # ----------------------------------------------------------------------
    NAME                                    = "Guid"
    CONSTRAINT_TYPE                         = GuidConstraint
    EXPRESSION_TYPES                        = None
