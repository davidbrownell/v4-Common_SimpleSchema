# ----------------------------------------------------------------------
# |
# |  ParseType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:11:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseType object"""

from dataclasses import dataclass
from typing import Optional

from Common_Foundation.Types import overridemethod

from .....Elements.Common.Cardinality import Cardinality
from .....Elements.Common.Element import Element
from .....Elements.Common.Metadata import Metadata

from .....Elements.Types.Impl.BaseType import BaseType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseType(BaseType):
    """Temporary type generated during parsing and replaced during subsequent steps"""

    # ----------------------------------------------------------------------
    cardinality: Cardinality
    unresolved_metadata: Optional[Metadata]

    # ----------------------------------------------------------------------
    @overridemethod
    def ToPython(self, *args, **kwargs):  # pylint: disable=unused-argument
        raise Exception("This method should never be called on ParseType instances.")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(ParseType, self)._GenerateAcceptDetails()

        yield "cardinality", self.cardinality

        if self.unresolved_metadata is not None:
            yield "metadata", self.unresolved_metadata
