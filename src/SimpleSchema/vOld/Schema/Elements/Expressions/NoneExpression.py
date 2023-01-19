# ----------------------------------------------------------------------
# |
# |  NoneExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:07:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneExpression object"""

from dataclasses import dataclass, field
from types import NoneType

from SimpleSchema.Schema.Elements.Expressions.FundamentalExpression import FundamentalExpression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneExpression(FundamentalExpression):
    """None expression"""

    # ----------------------------------------------------------------------
    NAME = "None"

    # ----------------------------------------------------------------------
    value: NoneType                         = field(init=False, default=None)
