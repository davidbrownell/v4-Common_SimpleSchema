# ----------------------------------------------------------------------
# |
# |  StringType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 14:09:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StringType type"""

import re

from dataclasses import dataclass, field
from functools import cached_property
from typing import ClassVar, Optional, Pattern, Tuple, Type as PythonType

from Common_Foundation.Types import overridemethod

from Common_FoundationEx.InflectEx import inflect

from ..FundamentalType import FundamentalType

from .....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StringType(FundamentalType):
    """A String"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "String"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (str, )

    min_length: int                                     = field(default=1)
    max_length: Optional[int]                           = field(default=None)

    validation_expression: Optional[str]                = field(default=None)

    _validation_regex: Optional[Pattern]                = field(init=False, compare=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.min_length < 0:
            raise ValueError("{} < 0".format(self.min_length))

        if self.max_length is not None and self.min_length > self.max_length:
            raise ValueError("{} > {}".format(self.min_length, self.max_length))

        if self.validation_expression is None:
            validation_regex = None
        else:
            validation_regex = re.compile(self.validation_expression)

        object.__setattr__(self, "_validation_regex", validation_regex)

        super(StringType, self).__post_init__()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _display_name(self) -> str:
        constraints: list[str] = []

        if self.min_length != 1:
            constraints.append(">= {}".format(inflect.no("character", self.min_length)))
        if self.max_length is not None:
            constraints.append("<= {}".format(inflect.no("character", self.max_length)))
        if self.validation_expression:
            constraints.append("'{}'".format(self.validation_expression))

        result = super(StringType, self)._display_name

        if not constraints:
            return result

        return "{} ({})".format(result, ", ".join(constraints))

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: str,
    ) -> str:
        num_chars = len(value)

        if num_chars < self.min_length:
            raise Exception(
                Errors.string_type_too_small.format(
                    value=inflect.no("character", self.min_length),
                    value_verb=inflect.plural_verb("was", self.min_length),
                    found=inflect.no("character", num_chars),
                    found_verb=inflect.plural_verb("was", num_chars),
                ),
            )

        if self.max_length is not None and num_chars > self.max_length:
            raise Exception(
                Errors.string_type_too_large.format(
                    value=inflect.no("character", self.max_length),
                    value_verb=inflect.plural_verb("was", self.max_length),
                    found=inflect.no("character", num_chars),
                    found_verb=inflect.plural_verb("was", num_chars),
                ),
            )

        if self._validation_regex is not None and not self._validation_regex.match(value):
            raise Exception(
                Errors.string_type_regex_failure.format(
                    value=value,
                    expression=self._validation_regex.pattern,
                ),
            )

        return value
