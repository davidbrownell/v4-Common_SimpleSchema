# ----------------------------------------------------------------------
# |
# |  IntegerExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 11:17:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IntegerExpression object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IntegerExpression(Expression):
    """Integer value"""

    # ----------------------------------------------------------------------
    value: int
