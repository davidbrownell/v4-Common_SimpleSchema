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
from typing import Optional
from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StringType(Type):
    min_length: Optional[int] = field(default=1)
    max_length: Optional[int] = field(default=None)
    validation_expression: Optional[str] = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.min_length is not None and self.min_length < 0:
            raise SimpleSchemaException(
                "'min_length' must be greater than or equal to '0' ('{}' was provided).".format(self.min_length),
                self.range,
            )

        if self.max_length is not None and self.max_length < 1:
            raise SimpleSchemaException(
                "'max_length' must be greater than or equal to '1' ('{}' was provided).".format(self.max_length),
                self.range,
            )

        if self.min_length is not None and self.max_length is not None and self.min_length > self.max_length:
            raise SimpleSchemaException("'min_length' > 'max_length'.", self.range)

        if (
            self.validation_expression is not None and
            (
                self.min_length is not None or self.max_length is not None
            )
        ):
            raise SimpleSchemaException("'validation_expression' cannot be used with 'min_length' and/or 'max_length'.", self.range)
