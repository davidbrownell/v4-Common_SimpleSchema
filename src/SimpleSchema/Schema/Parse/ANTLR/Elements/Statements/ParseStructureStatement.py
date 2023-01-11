# ----------------------------------------------------------------------
# |
# |  ParseStructureStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 10:43:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseStructureStatement object"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import cast, List, Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Statements.Statement import Statement

from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseType import ParseType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseTupleType import ParseTupleType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseVariantType import ParseVariantType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseStructureStatement(Statement):
    """A structure type"""

    CHILDREN_NAME                           = "children"

    # ----------------------------------------------------------------------
    name: Identifier
    base: Optional[ParseType]
    cardinality: Cardinality
    metadata: Optional[Metadata]
    children: List[Statement]  # Can be an empty list

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if isinstance(self.base, ParseVariantType):
            raise SimpleSchemaException("Base types cannot be variants.", self.base.range)
        elif isinstance(self.base, ParseTupleType):
            for child_type in self.base.types:
                if not isinstance(child_type, ParseIdentifierType):
                    raise SimpleSchemaException("Tuple base types may only contain identifiers.", child_type.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name

        if self.base:
            yield "base", self.base

        yield "cardinality", self.cardinality

        if self.metadata:
            yield "metadata", self.metadata

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield cast(List[Element], self.children)
