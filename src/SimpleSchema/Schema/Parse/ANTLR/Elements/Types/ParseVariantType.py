# ----------------------------------------------------------------------
# |
# |  ParseVariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-28 17:52:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseVariantType object"""

from dataclasses import dataclass
from functools import cached_property
from typing import cast, List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseType import ParseType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseVariantType(ParseType):
    """A list of types"""

    # ----------------------------------------------------------------------
    NAME = "ParseVariant"

    # ----------------------------------------------------------------------
    types: List[ParseType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

        for the_type in self.types:
            if isinstance(the_type, ParseVariantType):
                raise SimpleSchemaException("Nested variant types are not supported.", the_type.range)

    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def display_name(self) -> str:
        return "({})".format(" | ".join(the_type.display_name for the_type in self.types))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", cast(List[Element], self.types)

        yield from super(ParseVariantType, self)._GenerateAcceptDetails()
