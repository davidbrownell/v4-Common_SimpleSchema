# ----------------------------------------------------------------------
# |
# |  ParseTupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-28 17:48:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseTupleType object"""

from dataclasses import dataclass
from typing import List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Parse.ParseElements.Types.ParseType import ParseType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseTupleType(ParseType):
    """A list of types"""

    # ----------------------------------------------------------------------
    types: List[ParseType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", self.types

        yield from super(ParseTupleType, self)._GenerateAcceptDetails()
