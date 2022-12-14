# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
#
# The file has been automatically generated via ../Build.py using content
# in ../SimpleSchema.
#
# DO NOT MODIFY the contents of this file, as those changes will be
# overwritten the next time ../Build.py is invoked.
#
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NumberType(FundamentalType):
    # ----------------------------------------------------------------------
    NAME = "Number"

    # ----------------------------------------------------------------------
    class bitsEnum(str, Enum):
        Value16 = "IEEE 754 half precision"
        Value32 = "IEEE 754 single precision"
        Value64 = "IEEE 754 double precision"
        Value128 = "IEEE 754 quadruple precision"
        Value256 = "IEEE 754 octuple precision"

    # ----------------------------------------------------------------------
    min: Optional[float] = field(default=None)
    max: Optional[float] = field(default=None)
    bits: Optional[bitsEnum] = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(NumberType, self).__post_init__()

        if self.min is not None and self.max is not None and self.max < self.min:
            raise SimpleSchemaException("'min' > 'max'.", self.range)
