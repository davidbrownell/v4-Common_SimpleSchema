# ----------------------------------------------------------------------
# |
# |  Location.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 07:40:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Location object"""

from dataclasses import dataclass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Location(object):
    """Location within a source file"""

    # ----------------------------------------------------------------------
    line: int
    column: int

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.line <= 0:
            raise ValueError("Invalid line")
        if self.column <= 0:
            raise ValueError("Invalid column")

    # ----------------------------------------------------------------------
    def ToString(self) -> str:
        return "[{}, {}]".format(self.line, self.column)

    # ----------------------------------------------------------------------
    @staticmethod
    def Compare(
        this: "Location",
        that: "Location",
    ) -> int:
        result = this.line - that.line
        if result != 0:
            return result

        result = this.column - that.column
        if result != 0:
            return result

        return 0

    # ----------------------------------------------------------------------
    def __eq__(self, other): return self.__class__.Compare(self, other) == 0    # pylint: disable=multiple-statements
    def __ne__(self, other): return self.__class__.Compare(self, other) != 0    # pylint: disable=multiple-statements
    def __lt__(self, other): return self.__class__.Compare(self, other) < 0     # pylint: disable=multiple-statements
    def __le__(self, other): return self.__class__.Compare(self, other) <= 0    # pylint: disable=multiple-statements
    def __gt__(self, other): return self.__class__.Compare(self, other) > 0     # pylint: disable=multiple-statements
    def __ge__(self, other): return self.__class__.Compare(self, other) >= 0    # pylint: disable=multiple-statements
