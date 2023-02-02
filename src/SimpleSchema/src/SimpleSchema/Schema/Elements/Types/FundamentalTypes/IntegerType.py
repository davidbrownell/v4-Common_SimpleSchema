# ----------------------------------------------------------------------
# |
# |  IntegerType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 16:11:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IntegerType object"""

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import ClassVar, Optional, Tuple, Type as PythonType

from Common_Foundation.Types import overridemethod

from ..FundamentalType import FundamentalType

from ...Common.Cardinality import Cardinality
from ...Common.Metadata import Metadata

from .....Common import Errors
from .....Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IntegerType(FundamentalType):
    """An integer"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Integer"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (int, )

    # ----------------------------------------------------------------------
    # |  Public Types
    class BitsEnum(str, Enum):
        Value8                              = "8 bits"
        Value16                             = "16 bits"
        Value32                             = "32 bits"
        Value64                             = "64 bits"
        Value128                            = "128 bits"

    # ----------------------------------------------------------------------
    # |  Public Data
    min: Optional[int]                      = field(default=None)
    max: Optional[int]                      = field(default=None)
    bits: Optional[BitsEnum]                = field(default=None)

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        if self.min and self.max and self.min > self.max:
            raise ValueError("{} > {}".format(self.min, self.max))

        super(IntegerType, self).__post_init__()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _display_name(self) -> str:
        constraints: list[str] = []

        if self.min is not None:
            constraints.append(">= {}".format(self.min))
        if self.max is not None:
            constraints.append("<= {}".format(self.max))

        result = super(IntegerType, self)._display_name

        if not constraints:
            return result

        return "{} ({})".format(result, ", ".join(constraints))

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "IntegerType":
        return IntegerType(range_value, cardinality, metadata, self.min, self.max, self.bits)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: int,
    ) -> int:
        if self.min is not None and value < self.min:
            raise Exception(
                Errors.integer_type_too_small.format(
                    constraint=self.min,
                    value=value,
                ),
            )
        if self.max is not None and value > self.max:
            raise Exception(
                Errors.integer_type_too_large.format(
                    constraint=self.max,
                    value=value,
                ),
            )

        return value
