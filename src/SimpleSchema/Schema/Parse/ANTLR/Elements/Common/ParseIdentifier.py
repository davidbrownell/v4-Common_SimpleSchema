# ----------------------------------------------------------------------
# |
# |  ParseIdentifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:25:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseIdentifier type"""

from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from .....Elements.Common.Element import Element
from .....Elements.Common.SimpleElement import SimpleElement
from .....Elements.Common.Visibility import Visibility

from ......Common import Errors
from ......Common.Range import Location, Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIdentifier(Element):
    """Identifier generated during parsing and replaced in subsequent steps"""

    # ----------------------------------------------------------------------
    value: str

    _first_char: str                        = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        first_char = self.__class__._GetFirstChar(self.value)  # pylint: disable=protected-access

        if first_char is None:
            raise Errors.ParseIdentifierNoChars.Create(self.range, self.value)

        if not (
            ('a' <= first_char <= 'z')
            or ('A' <= first_char <= 'Z')
        ):
            raise Errors.ParseIdentifierNotAlpha.Create(self.range, self.value)

        # Commit
        object.__setattr__(self, "_first_char", first_char)

    # ----------------------------------------------------------------------
    @cached_property
    def is_expression(self) -> bool:
        return self._first_char.islower()

    @cached_property
    def is_type(self) -> bool:
        return self._first_char.isupper()

    @cached_property
    def visibility(self) -> SimpleElement[Visibility]:
        range_value: Optional[Range] = None

        if self.value[0] == "_":
            visibility = Visibility.Private
        elif self.value[0] in ["@", "$", "&"]:
            visibility = Visibility.Protected
        else:
            visibility = Visibility.Public
            range_value = self.range

        if range_value is None:
            range_value = Range(
                self.range.filename,
                self.range.begin,
                Location(self.range.begin.line, self.range.begin.column + 1),
            )

        return SimpleElement[Visibility](range_value, visibility)

    # ----------------------------------------------------------------------
    def ToSimpleElement(self) -> SimpleElement[str]:
        return SimpleElement[str](self.range, self.value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _GetFirstChar(
        value: str,
    ) -> Optional[str]:
        for char in value:
            if char not in ["_", "@", "$", "&"]:
                return char

        return None
