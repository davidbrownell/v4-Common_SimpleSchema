# ----------------------------------------------------------------------
# |
# |  ParseStructureStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 10:43:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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

from SimpleSchema.Schema.Elements.Statements.Statement import Statement

from SimpleSchema.Schema.Parse.ParseElements.Types.ParseType import ParseType


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
