# ----------------------------------------------------------------------
# |
# |  Identifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 10:37:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Identifier object"""

from dataclasses import dataclass
from functools import cached_property

from SimpleSchema.Schema.Impl.Common.Element import Element
from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Identifier(Element):
    """Mixin for IdentifierType and IdentifierExpression objects"""

    # ----------------------------------------------------------------------
    value: str

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if (
            not self.value
            or self.value == "_"
            or not (
                'a' <= self._first_char <= 'z'
                or 'A' <= self._first_char <= 'Z'
            )
        ):
            raise SimpleSchemaException(
                "'{}' is not a valid identifier.".format(self.value),
                self.range,
            )

    # ----------------------------------------------------------------------
    @cached_property
    def is_expression(self) -> bool:
        return self._first_char.islower()

    @cached_property
    def is_type(self) -> bool:
        return self._first_char.isupper()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _first_char(self) -> str:
        if self.value.startswith("_"):
            return self.value[1]

        return self.value[0]
