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
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IntegerType(Type):
    class bitsEnum(str, Enum):
        Value8 = "8 bits"
        Value16 = "16 bits"
        Value32 = "32 bits"
        Value64 = "64 bits"
        Value128 = "128 bits"

    min: Optional[int] = field(default=None)
    max: Optional[int] = field(default=None)
    bits: Optional[bitsEnum] = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.min is not None and self.max is not None and self.max < self.min:
            raise SimpleSchemaException("'min' > 'max'.", self.range)
