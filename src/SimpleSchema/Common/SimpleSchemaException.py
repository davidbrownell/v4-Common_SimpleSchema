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

import itertools
import textwrap

from dataclasses import dataclass, InitVar, make_dataclass
from typing import ClassVar, Iterable, Type as PythonType, Union

from .Range import Range


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class SimpleSchemaException(Exception):
    """Base class for exceptions thrown within SimpleSchema"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        range_or_ranges: Union[Range, Iterable[Range]],
        message: str,
    ):
        super(SimpleSchemaException, self).__init__(message)

        ranges: list[Range] = []

        if isinstance(range_or_ranges, Range):
            ranges.append(range_or_ranges)
        elif isinstance(range_or_ranges, list):
            ranges += range_or_ranges
        else:
            assert False, range_or_ranges  # pragma: no cover

        object.__setattr__(self, "_ranges", ranges)

    # ----------------------------------------------------------------------
    @property
    def ranges(self) -> list[Range]:
        return self._ranges  # type: ignore  # pylint: disable=no-member

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        message = super(SimpleSchemaException, self).__str__()

        if len(self.ranges) == 1 and "\n" not in message:
            message = "{} ({})".format(message, self.ranges[0])
        else:
            message = textwrap.dedent(
                """\
                {}

                {}
                """,
            ).format(
                message.rstrip(),
                "\n".join("    - {}".format(range_value) for range_value in self.ranges),
            )

        return message


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicSimpleSchemaException(SimpleSchemaException):
    """SimpleSchemaException that is generated dynamically"""

    # ----------------------------------------------------------------------
    MESSAGE_TEMPLATE: ClassVar[str]         = ""

    # ----------------------------------------------------------------------
    @staticmethod
    def CreateType(
        message_template: str,
        **args: PythonType,
    ) -> PythonType["DynamicSimpleSchemaException"]:
        dynamic_fields_class = make_dataclass(
            "DynamicFields",
            itertools.chain(
                [
                    ("range_or_ranges", InitVar[Union[Range, Iterable[Range]]]),
                ],
                args.items(),
            ),
            bases=(DynamicSimpleSchemaException, ),
            frozen=True,
            repr=False,
        )

        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class Final(dynamic_fields_class):  # type: ignore
            # ----------------------------------------------------------------------
            MESSAGE_TEMPLATE: ClassVar[str]             = message_template

            # ----------------------------------------------------------------------
            def __post_init__(
                self,
                range_or_ranges: Union[Range, Iterable[Range]],
            ):
                super(Final, self).__post_init__()

                SimpleSchemaException.__init__(
                    self,
                    range_or_ranges,
                    self.__class__.MESSAGE_TEMPLATE.format(**self.__dict__),
                )

        # ----------------------------------------------------------------------

        return Final

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs) -> "SimpleSchemaException":
        # pylint has problems with dynamically created classes based on this base,
        # as it thinks that there should only be 1 positional argument. This hack
        # will eliminate that error.
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.MESSAGE_TEMPLATE, "Make sure to define MESSAGE_TEMPLATE."
