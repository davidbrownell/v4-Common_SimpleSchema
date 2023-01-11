# ----------------------------------------------------------------------
# |
# |  NumberExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 11:44:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NumberExpression object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NumberExpression(Expression):
    """Number Value"""

    # ----------------------------------------------------------------------
    NAME = "Number"

    # ----------------------------------------------------------------------
    value: float
