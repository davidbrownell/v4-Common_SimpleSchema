# ----------------------------------------------------------------------
# |
# |  StructureType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-09 14:58:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StructureType object"""

from dataclasses import dataclass
from functools import cached_property
from typing import Optional, TYPE_CHECKING

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range

from SimpleSchema.Schema.Elements.Types.Type import Type

if TYPE_CHECKING:
    from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StructureType(Type):
    """A structure that is used as a type"""

    # ----------------------------------------------------------------------
    NAME = "Structure"

    # ----------------------------------------------------------------------
    statement: "StructureStatement"

    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def display_name(self) -> str:
        return self.statement.name.id.value

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "statement", self.statement

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateAcceptReferenceDetails(self) -> Element:
        return SimpleElement(
            self.statement.range,
            self.statement.name.id.value,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> Type:
        return StructureType(range_value, cardinality, metadata, self.statement)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ParseExpressionImpl(self, *args, **kwargs):
        raise Exception("A structure cannot be created from an expression.")
