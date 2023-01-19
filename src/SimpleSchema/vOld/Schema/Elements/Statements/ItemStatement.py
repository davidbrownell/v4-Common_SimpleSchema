# ----------------------------------------------------------------------
# |
# |  ItemStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-04 12:02:40
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
from weakref import ref, ReferenceType
from typing import cast

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier

from SimpleSchema.Schema.Elements.Statements.Statement import Statement

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ItemStatement(Statement):
    """Defines a single item"""

    # ----------------------------------------------------------------------
    GENERATES_DETAILS_REFERENCES            = True

    # ----------------------------------------------------------------------
    name: Identifier
    type: Type

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "type", cast(ReferenceType[Element], ref(self.type))
