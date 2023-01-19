# ----------------------------------------------------------------------
# |
# |  SimpleSchemaException.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 16:37:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SimpleSchemaException object"""

import textwrap

from typing import Iterable, List, Union

from SimpleSchema.Schema.Elements.Common.Range import Range


# ----------------------------------------------------------------------
class SimpleSchemaException(Exception):
    """Exception raise during simple schema parsing and validation"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        msg: str,
        range_or_ranges: Union[Range, Iterable[Range]],
    ) -> None:
        super(SimpleSchemaException, self).__init__(msg)

        ranges: List[Range] = []

        if isinstance(range_or_ranges, Range):
            ranges.append(range_or_ranges)
        else:
            ranges += range_or_ranges

        self.ranges                         = ranges

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        message = super(SimpleSchemaException, self).__str__()

        if len(self.ranges) == 1:
            if "\n" in message:
                return textwrap.dedent(
                    """\
                    {}

                    {}
                    """,
                ).format(
                    message.rstrip(),
                    self.ranges[0].ToString(),
                )

            return "{} ({})".format(message, self.ranges[0].ToString())

        return textwrap.dedent(
            """\
            {}

            {}
            """,
        ).format(message, "\n".join("    - {}".format(range.ToString()) for range in self.ranges))
