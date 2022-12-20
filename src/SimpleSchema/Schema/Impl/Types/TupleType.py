# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 18:18:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

from dataclasses import dataclass
from typing import List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Impl.Common.Element import Element
from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException
from SimpleSchema.Schema.Impl.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleType(Type):
    """A list of types"""

    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

        for the_type in self.types:
            if isinstance(the_type, TupleType):
                raise SimpleSchemaException("Nested tuple types are not supported.", the_type.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", self.types

        yield from super(TupleType, self)._GenerateAcceptDetails()
