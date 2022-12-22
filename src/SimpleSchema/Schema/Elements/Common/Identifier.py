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

from dataclasses import dataclass, field
from enum import auto, Enum
from functools import cached_property
from typing import Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
class Visibility(Enum):
    """Access restriction associated with an Identifier"""

    Public                                  = auto()
    Protected                               = auto()
    Private                                 = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Identifier(Element):
    """Mixin for IdentifierType and IdentifierExpression objects"""

    # ----------------------------------------------------------------------
    id: SimpleElement[str]
    visibility: SimpleElement[Visibility]

    _first_char: str                        = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        first_char = self.__class__._GetFirstChar(self.id.value)  # pylint: disable=protected-access

        if first_char is None:
            raise SimpleSchemaException(
                "'{}' is not a valid identifier.".format(self.id.value),
                self.range,
            )

        if not (
            ('a' <= first_char <= 'z')
            or ('A' <= first_char <= 'Z')
        ):
            raise SimpleSchemaException(
                "'{}' is not a valid identifier.".format(self.id.value),
                self.range,
            )

        # Commit
        object.__setattr__(self, "_first_char", first_char)

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
    @staticmethod
    def _GetFirstChar(
        value: str,
    ) -> Optional[str]:
        for char in value:
            if char not in ['_', '@', '$', '&']:
                return char

        return None

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "id", self.id
        yield "visibility", self.visibility
