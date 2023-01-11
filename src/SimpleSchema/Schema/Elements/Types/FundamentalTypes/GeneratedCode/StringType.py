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

import re
from dataclasses import dataclass, field
from typing import Optional
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StringType(FundamentalType):
    # ----------------------------------------------------------------------
    NAME = "String"

    # ----------------------------------------------------------------------
    min_length: int = field(default=1)
    max_length: Optional[int] = field(default=None)
    validation_expression: Optional[str] = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(StringType, self).__post_init__()

        if self.min_length < 0:
            raise SimpleSchemaException("'min_length' must be greater than or equal to '0' ('{}' was provided).".format(self.min_length), self.range)

        if self.max_length is not None:
            if self.max_length < 1:
                raise SimpleSchemaException("'max_length' must be greater than or equal to '1' ('{}' was provided).".format(self.max_length), self.range)

            if self.min_length > self.max_length:
                raise SimpleSchemaException("'max_length' < 'min_length'.", self.range)

        if self.validation_expression is not None:
            if self.max_length is not None:
                raise SimpleSchemaException("'validation_expression' cannot be used with 'max_length'.", self.range)

            try:
                re.compile(self.validation_expression)
            except re.error as ex:
                raise SimpleSchemaException("'{}' is not a valid regular expression: {}.".format(self.validation_expression, ex), self.range) from ex
