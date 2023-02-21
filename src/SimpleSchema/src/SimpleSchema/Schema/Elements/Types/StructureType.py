# ----------------------------------------------------------------------
# |
# |  StructureType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-13 12:17:33
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
from typing import Any, ClassVar, Tuple, Type as PythonType

from Common_Foundation.Types import overridemethod

from .BasicType import BasicType

from ..Common.Element import Element

from ..Statements.StructureStatement import StructureStatement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StructureType(BasicType):
    """Type based on a StructureStatement"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Structure"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    structure: StructureStatement

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @property
    def _display_type(self) -> str:
        return self.structure.name.value

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "structure", self.structure

    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: Any,  # pylint: disable=unused-argument
    ) -> Any:
        raise Exception("This method should never be called for StructureType instances.")
