# ----------------------------------------------------------------------
# |
# |  IdentifierType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:50:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IdentifierType object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Impl.Common.Identifier import Identifier
from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Impl.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IdentifierType(Identifier, Type):
    """Type associated with an IdentifierExpression"""

    # ----------------------------------------------------------------------
    def __post_init__(self):
        Identifier.__post_init__(self)

        if not self.is_type:
            raise SimpleSchemaException("'{}' is not a valid type; identifier types must begin with an uppercase letter.".format(self.value), self.range)
