# ----------------------------------------------------------------------
# |
# |  TypeConversionKey.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-11 12:41:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeConversionKey object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeConversionKey(object):
    """\
    Type used to capture the state of a single step when converting from a `ParseType` to standard `Type`.
    This information is used to detect cycles in `StructureStatement` objects.
    """

    name: str
    range: Range

    # ----------------------------------------------------------------------
    @classmethod
    def FromIdentifier(
        cls,
        identifier: Identifier,
    ) -> "TypeConversionKey":
        return cls(identifier.id.value, identifier.id.range)
