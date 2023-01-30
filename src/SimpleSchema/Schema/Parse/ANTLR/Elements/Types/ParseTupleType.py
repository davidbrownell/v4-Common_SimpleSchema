# ----------------------------------------------------------------------
# |
# |  ParseTupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 11:02:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseTupleType object"""

from dataclasses import dataclass
from functools import cached_property
from typing import cast, ClassVar, Optional

from Common_Foundation.Types import overridemethod

from .ParseType import ParseType

from .....Elements.Common.Cardinality import Cardinality
from .....Elements.Common.Element import Element
from .....Elements.Common.Metadata import Metadata

from ......Common import Errors
from ......Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseTupleType(ParseType):
    """A list of types used during the parsing process; subsequent steps will overwrite this value"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "ParseTuple"

    types: list[ParseType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise Errors.ParseTupleTypeMissingTypes.Create(self.range)

        super(ParseTupleType, self).__post_init__()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _display_name(self) -> str:
        return "_({}, )".format(", ".join(the_type.display_name for the_type in self.types))

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(ParseTupleType, self)._GenerateAcceptDetails()

        yield "types", cast(list[Element], self.types)

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "ParseTupleType":
        return ParseTupleType(range_value, cardinality, metadata, self.types)
