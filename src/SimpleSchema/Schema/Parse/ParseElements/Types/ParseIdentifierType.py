# ----------------------------------------------------------------------
# |
# |  ParseIdentifierType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-28 16:42:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseIdentifierType object"""

from dataclasses import dataclass
from typing import List, Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Parse.ParseElements.Types.ParseType import ParseType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIdentifierType(ParseType):
    """Temporary identifier type generated during Parsing and replaced during subsequent steps"""

    # ----------------------------------------------------------------------
    identifiers: List[Identifier]
    is_global_reference: Optional[Range]
    is_element_reference: Optional[Range]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.identifiers:
            raise SimpleSchemaException(
                "Identifier type instances must have at least one identifier.",
                self.range,
            )

        for identifier in self.identifiers:
            if not identifier.is_type:
                raise SimpleSchemaException(
                    "'{}' is not a valid type; identifier types must begin with an uppercase letter.".format(identifier.id.value),
                    identifier.id.range,
                )

        if self.is_global_reference and len(self.identifiers) > 1:
            raise SimpleSchemaException(
                "There may only be one identifier for types that are global references.",
                self.is_global_reference,
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "identifiers", self.identifiers

        yield from super(ParseIdentifierType, self)._GenerateAcceptDetails()
