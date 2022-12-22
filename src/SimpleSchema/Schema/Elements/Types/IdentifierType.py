# ----------------------------------------------------------------------
# |
# |  IdentifierType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:50:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IdentifierType object"""

from dataclasses import dataclass
from typing import List, Optional

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, Visibility
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Types.Type import Type

from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IdentifierType(Type):
    """Type associated with an IdentifierExpression"""

    # ----------------------------------------------------------------------
    identifiers: List[Identifier]
    element_reference: Optional[Range]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.identifiers:
            raise SimpleSchemaException(
                "'IdentifierType' instances must have at least one identifier.",
                self.range,
            )

        for identifier_index, identifier in enumerate(self.identifiers):
            if not identifier.is_type:
                raise SimpleSchemaException(
                    "'{}' is not a valid type; identifier types must begin with an uppercase letter.".format(identifier.id.value),
                    identifier.id.range,
                )

            if identifier_index != 0:
                if identifier.visibility.value == Visibility.Private:
                    raise SimpleSchemaException(
                        "'{}' is private and cannot be accessed.".format(identifier.id.value),
                        identifier.visibility.range,
                    )

                if identifier.visibility.value == Visibility.Protected:
                    raise SimpleSchemaException(
                        "'{}' is protected and cannot be accessed.".format(identifier.id.value),
                        identifier.visibility.range,
                    )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "identifiers", self.identifiers

        yield from super(IdentifierType, self)._GenerateAcceptDetails()
