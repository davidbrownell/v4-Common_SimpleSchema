# ----------------------------------------------------------------------
# |
# |  Visibility.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 20:50:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visibility and VisibilityTrait objects"""

from dataclasses import dataclass
from enum import auto, Enum

from Common_Foundation.Types import overridemethod

from .Element import Element
from .SimpleElement import SimpleElement


# ----------------------------------------------------------------------
class Visibility(Enum):
    """Access restriction for a statement"""

    Public                                  = auto()
    Protected                               = auto()
    Private                                 = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VisibilityTrait(object):
    """Trait for Elements that have a visibility attribute"""

    visibility: SimpleElement[Visibility]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "visibility", self.visibility
