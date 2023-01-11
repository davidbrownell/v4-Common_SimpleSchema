# ----------------------------------------------------------------------
# |
# |  StructureStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-09 00:30:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StructureStatement object"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import cast, List
from weakref import ref, ReferenceType

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier

from SimpleSchema.Schema.Elements.Statements.Statement import Statement

from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Types.StructureType import StructureType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StructureStatement(Statement):
    """The definition of a structure"""

    # ----------------------------------------------------------------------
    CHILDREN_NAME                           = "children"
    GENERATES_DETAILS_REFERENCES            = True

    # ----------------------------------------------------------------------
    name: Identifier
    bases: List[Type]  # Can be any empty list
    children: List[Statement]  # Can be an empty list

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.bases:
            # TODO: Don't assert, make better error messages

            if len(self.bases) == 1:
                with self.bases[0].Resolve() as base_type:
                    assert isinstance(base_type, (FundamentalType, StructureType)), self.bases
            else:
                for base_type in self.bases:
                    with base_type.Resolve() as base_type:
                        assert isinstance(base_type, StructureType), base_type

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "bases", cast(List[ReferenceType["Element"]], [ref(base) for base in self.bases])

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield cast(List[Element], self.children)
