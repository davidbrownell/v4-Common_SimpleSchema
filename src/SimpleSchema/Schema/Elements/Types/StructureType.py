# ----------------------------------------------------------------------
# |
# |  StructureType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-24 12:46:31
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
from typing import Any, cast, ClassVar, Optional, Tuple, Type as PythonType, TYPE_CHECKING
from weakref import ref, ReferenceType

from Common_Foundation.Types import overridemethod

from .Type import Type

from ..Common.Cardinality import Cardinality
from ..Common.Element import Element
from ..Common.Metadata import Metadata

from ....Common.Range import Range

if TYPE_CHECKING:
    from ..Statements.StructureStatement import StructureStatement  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StructureType(Type):
    """A variable that points to a structure definition"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Structure"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    statement: "StructureStatement"

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _display_name(self) -> str:
        return self.statement.name.value

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(StructureType, self)._GenerateAcceptDetails()

        yield "statement", cast(ReferenceType[Element], ref(self.statement))

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "StructureType":
        return StructureType(range_value, cardinality, metadata, self.statement)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Any,  # pylint: disable=unused-argument
    ) -> Any:
        raise Exception("This method should never be called for StructureType instances.")
