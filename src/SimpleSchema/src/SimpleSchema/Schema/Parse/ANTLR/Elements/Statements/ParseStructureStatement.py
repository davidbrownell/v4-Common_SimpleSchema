# ----------------------------------------------------------------------
# |
# |  ParseStructureStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 10:50:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseStructureStatement object"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import cast, ClassVar, Optional

from Common_Foundation.Types import overridemethod

from ..Common.ParseIdentifier import ParseIdentifier

from ..Types.ParseIdentifierType import ParseIdentifierType

from .....Elements.Common.Cardinality import Cardinality
from .....Elements.Common.Metadata import Metadata

from .....Elements.Statements.Statement import Element, Statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseStructureStatement(Statement):
    """A structure-like statement that is used during the parsing process"""

    # ----------------------------------------------------------------------
    CHILDREN_NAME: ClassVar[str]            = "children"

    name: ParseIdentifier
    bases: Optional[list[ParseIdentifierType]]
    cardinality: Cardinality
    metadata: Optional[Metadata]
    children: list[Statement]  # Can be Empty

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name

        if self.bases:
            yield "bases", cast(list[Element], self.bases)

        yield "cardinality", self.cardinality

        if self.metadata:
            yield "metadata", self.metadata

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield cast(list[Element], self.children)
