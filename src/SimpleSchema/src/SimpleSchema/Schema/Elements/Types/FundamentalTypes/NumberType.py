# ----------------------------------------------------------------------
# |
# |  NumberType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 16:50:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NumberType object"""

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import ClassVar, Optional, Tuple, Type as PythonType, Union

from Common_Foundation.Types import overridemethod

from ..FundamentalType import FundamentalType

from .....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NumberType(FundamentalType):
    """A number"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Number"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (float, int, )

    # ----------------------------------------------------------------------
    # |  Public Types
    class BitsEnum(str, Enum):
        Value16                             = "IEEE 754 half precision"
        Value32                             = "IEEE 754 single precision"
        Value64                             = "IEEE 754 double precision"
        Value128                            = "IEEE 754 quadruple precision"
        Value256                            = "IEEE 754 octuple precision"

    # ----------------------------------------------------------------------
    # |  Public Data
    min: Optional[float]                    = field(default=None)
    max: Optional[float]                    = field(default=None)
    bits: Optional[BitsEnum]                = field(default=None)

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        if self.min and self.max and self.min > self.max:
            raise ValueError("{} > {}".format(self.min, self.max))

        super(NumberType, self).__post_init__()

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

        result = super(NumberType, self)._display_name

        if not constraints:
            return result

        return "{} ({})".format(result, ", ".join(constraints))

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Union[float, int],
    ) -> float:
        value = float(value)

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
