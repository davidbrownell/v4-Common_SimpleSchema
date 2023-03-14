# ----------------------------------------------------------------------
# |
# |  ItemStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-24 12:28:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ItemStatement object"""

from dataclasses import dataclass
from typing import cast, TYPE_CHECKING
from weakref import ref, ReferenceType as WeakReferenceType

from Common_Foundation.Types import overridemethod

from .Statement import Statement

from ..Common.Element import Element
from ..Common.SimpleElement import SimpleElement
from ..Common.Visibility import VisibilityTrait

if TYPE_CHECKING:
    from ..Types.ReferenceType import ReferenceType  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ItemStatement(VisibilityTrait, Statement):
    """Defines a single variable item"""

    # ----------------------------------------------------------------------
    name: SimpleElement[str]
    type: "ReferenceType"

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from VisibilityTrait._GenerateAcceptDetails(self)

        yield "name", self.name
        yield "type", cast(WeakReferenceType[Element], ref(self.type))
