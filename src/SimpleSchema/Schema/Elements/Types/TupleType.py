# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-04 14:24:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

from dataclasses import dataclass
from functools import cached_property
from typing import cast, List, Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElements
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleType(Type):
    """A list of types"""

    # ----------------------------------------------------------------------
    NAME = "Tuple"

    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def display_name(self) -> str:
        return "({}, )".format(", ".join(the_type.display_name for the_type in self.types))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", cast(List[Element], self.types)

        yield from super(TupleType, self)._GenerateAcceptDetails()

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateAcceptReferenceDetails(self) -> Element:
        return SimpleElements(
            self.range,
            [
                child_type._CreateAcceptReferenceDetails()  # pylint: disable=protected-access
                for child_type in self.types
            ],
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> Type:
        return TupleType(range_value, cardinality, metadata, self.types)
