# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 09:35:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType"""

from dataclasses import dataclass
from typing import List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariantType(Type):
    """A list of potential types"""

    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

        for the_type in self.types:
            if isinstance(the_type, VariantType):
                raise SimpleSchemaException("Nested variant types are not supported.", the_type.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", self.types

        yield from super(VariantType, self)._GenerateAcceptDetails()
