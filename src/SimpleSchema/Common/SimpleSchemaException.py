# ----------------------------------------------------------------------
# |
# |  SimpleSchemaException.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 19:46:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Exception object"""

import textwrap

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar, make_dataclass
from functools import cached_property
from typing import Iterable, Type, Union

from Common_Foundation.Types import overridemethod

from .Range import Range


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SimpleSchemaException(ABC, Exception):
    """Exception raised within SimpleSchema"""

    range_or_ranges: InitVar[Union[Range, Iterable[Range]]]
    ranges: list[Range]                     = field(init=False)

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs) -> "SimpleSchemaException":
        # pylint has problems with dynamically created classes based on this base,
        # as it thinks that there should only be 1 positional argument. This hack
        # will eliminate that error.
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        range_or_ranges: Union[Range, Iterable[Range]],
    ):
        ranges: list[Range] = []

        if isinstance(range_or_ranges, Range):
            ranges.append(range_or_ranges)
        elif isinstance(range_or_ranges, list):
            ranges += range_or_ranges
        else:
            assert False, range_or_ranges  # pragma: no cover

        object.__setattr__(self, "ranges", ranges)

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        return self._string

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _string(self) -> str:
        message = self._message_template.format(**self.__dict__)

        if len(self.ranges) == 1 and "\n" not in message:
            return "{} ({})".format(message, self.ranges[0])

        return textwrap.dedent(
            """\
            {}

            {}
            """,
        ).format(
            message.rstrip(),
            "\n".join("    - {}".format(range_value) for range_value in self.ranges),
        )

    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def _message_template(self) -> str:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreateExceptionType(
    message_template: str,
    **args: Type,
) -> Type[SimpleSchemaException]:
    dynamic_fields_class = make_dataclass(
        "DynamicFields",
        args.items(),
        bases=(SimpleSchemaException, ),
        frozen=True,
        repr=False,
    )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class Final(dynamic_fields_class):  # type: ignore
        # ----------------------------------------------------------------------
        @property
        @overridemethod
        def _message_template(self) -> str:
            return message_template

    # ----------------------------------------------------------------------

    return Final
