# ----------------------------------------------------------------------
# |
# |  FundamentalExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:16:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FundamentalExpression object"""

from dataclasses import dataclass
from typing import Any

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FundamentalExpression(Expression):
    """Abstract base class for Expressions that resolve to a FundamentalType"""

    # ----------------------------------------------------------------------
    value: Any
