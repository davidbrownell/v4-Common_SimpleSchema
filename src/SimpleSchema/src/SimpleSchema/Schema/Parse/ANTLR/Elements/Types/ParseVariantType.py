# ----------------------------------------------------------------------
# |
# |  ParseVariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 11:23:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseVariantType object"""

from dataclasses import dataclass
from typing import cast

from Common_Foundation.Types import overridemethod

from .ParseType import ParseType

from .....Elements.Common.Element import Element

from ......Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseVariantType(ParseType):
    """A list of types used during the parsing process; subsequent steps will overwrite this value"""

    # ----------------------------------------------------------------------
    types: list[ParseType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if len(self.types) < 2:
            raise Errors.ParseVariantTypeMissingTypes.Create(self.range)

        for the_type in self.types:
            if isinstance(the_type, ParseVariantType):
                raise Errors.ParseVariantTypeNestedType.Create(the_type.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", cast(list[Element], self.types)

        yield from super(ParseVariantType, self)._GenerateAcceptDetails()

    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def _display_type(self) -> str:
        return "({}){}".format(
            " | ".join(child_type.display_type for child_type in self.types),
            self.cardinality,
        )
