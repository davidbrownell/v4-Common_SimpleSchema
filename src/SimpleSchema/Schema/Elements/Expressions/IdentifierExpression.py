# ----------------------------------------------------------------------
# |
# |  IdentifierExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:34:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IdentifierExpression object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IdentifierExpression(Identifier, Expression):
    """An identifier that can be used to represent a data instance- or type-name"""

    # ----------------------------------------------------------------------
    def __post_init__(self):
        Identifier.__post_init__(self)

        if not self.is_expression:
            raise SimpleSchemaException("'{}' is not a valid expression; identifier expressions must begin with a lowercase letter.".format(self.id.value), self.range)
