# ----------------------------------------------------------------------
# |
# |  ParseIdentifierType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:15:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseIdentifierType object"""

from dataclasses import dataclass
from functools import cached_property
from typing import cast, ClassVar, Optional

from Common_Foundation.Types import overridemethod

from .ParseType import ParseType

from ..Common.ParseIdentifier import ParseIdentifier

from .....Elements.Common.Element import Element

from ......Common import Errors
from ......Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIdentifierType(ParseType):
    """Temporary identifier generated during parsing and replaced in subsequent steps"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "ParseIdentifier"

    # ----------------------------------------------------------------------
    identifiers: list[ParseIdentifier]
    is_global_reference: Optional[Range]
    is_item_reference: Optional[Range]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(ParseIdentifierType, self).__post_init__()

        if not self.identifiers:
            raise Errors.ParseIdentifierTypeEmpty.Create(self.range)

        for identifier in self.identifiers:
            if not identifier.is_type:
                raise Errors.ParseIdentifierTypeNotType.Create(identifier.range, identifier.value)

        if self.is_global_reference and len(self.identifiers) > 1:
            raise Errors.ParseIdentifierTypeInvalidGlobal.Create(self.is_global_reference)

    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def display_name(self) -> str:
        result = ".".join(identifier.value for identifier in self.identifiers)

        if self.is_global_reference:
            result = "::{}".format(result)
        if self.is_item_reference:
            result = "{}::item".format(result)

        return result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "identifiers", cast(list[Element], self.identifiers)

        yield from super(ParseIdentifierType, self)._GenerateAcceptDetails()
