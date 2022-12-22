# ----------------------------------------------------------------------
# |
# |  StringExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 12:38:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StringExpression object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StringExpression(Expression):
    """String value"""

    # ----------------------------------------------------------------------
    value: str
