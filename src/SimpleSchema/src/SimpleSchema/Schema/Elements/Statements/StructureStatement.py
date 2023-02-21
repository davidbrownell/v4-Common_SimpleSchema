# ----------------------------------------------------------------------
# |
# |  StructureStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 10:11:54
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
from typing import cast, ClassVar, TYPE_CHECKING
from weakref import ref, ReferenceType as WeakReferenceType

from Common_Foundation.Types import overridemethod

from .Statement import Statement

from ..Common.Element import Element
from ..Common.SimpleElement import SimpleElement
from ..Common.Visibility import Visibility

if TYPE_CHECKING:
    from ..Types.ReferenceType import ReferenceType  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StructureStatement(Statement):
    """The definition of a structure"""

    # ----------------------------------------------------------------------
    CHILDREN_NAME: ClassVar[str]            = "children"

    visibility: SimpleElement[Visibility]
    name: SimpleElement[str]
    base_types: list["ReferenceType"]       # Can be an empty list
    children: list[Statement]               # Can be an empty list

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "visibility", self.visibility
        yield "name", self.name

        if self.base_types:
            yield "base_types", cast(list[WeakReferenceType[Element]], [ref(base_type) for base_type in self.base_types])

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield cast(list[Element], self.children)
