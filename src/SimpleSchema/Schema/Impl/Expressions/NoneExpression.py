# ----------------------------------------------------------------------
# |
# |  NoneExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 11:58:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneExpression object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Impl.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneExpression(Expression):
    """Encapsulates the concept of None"""

    pass
