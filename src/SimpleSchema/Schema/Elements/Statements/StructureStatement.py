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
from typing import cast, ClassVar, Optional
from weakref import ref, ReferenceType

from Common_Foundation.Types import overridemethod

from .Statement import Statement

from ..Common.Element import Element
from ..Common.Metadata import Metadata
from ..Common.SimpleElement import SimpleElement
from ..Common.Visibility import Visibility

from ..Types.FundamentalType import FundamentalType
from ..Types.Type import Type
from ..Types.StructureType import StructureType

from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StructureStatement(Statement):
    """The definition of a structure"""

    # ----------------------------------------------------------------------
    CHILDREN_NAME: ClassVar[str]            = "children"

    visibility: SimpleElement[Visibility]
    name: SimpleElement[str]
    base_types: list[Type]                  # Can be an empty list
    metadata: Optional[Metadata]
    children: list[Statement]               # Can be an empty list

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if len(self.base_types) == 1:
            with self.base_types[0].Resolve() as resolved_base_type:
                if not isinstance(resolved_base_type, (FundamentalType, StructureType)):
                    raise Errors.StructureStatementInvalidSingleBase.Create(self.base_types[0].range)
        else:
            for base_type in self.base_types:
                with base_type.Resolve() as resolved_base_type:
                    if not isinstance(resolved_base_type, StructureType):
                        raise Errors.StructureStatementInvalidBase.Create(base_type.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "visibility", self.visibility
        yield "name", self.name

        if self.base_types:
            yield "base_types", cast(list[ReferenceType[Element]], [ref(base_type) for base_type in self.base_types])

        if self.metadata:
            yield "metadata", self.metadata

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield cast(list[Element], self.children)
