# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 09:35:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType"""

from dataclasses import dataclass
from typing import List

from SimpleSchema.Schema.Impl.Types.IdentifierType import IdentifierType, SimpleSchemaException, Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariantType(Type):
    """A list of potential types"""

    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

        for the_type in self.types:
            if not isinstance(the_type, IdentifierType):
                raise SimpleSchemaException("Nested variant types must be identifier types.", the_type.range)
