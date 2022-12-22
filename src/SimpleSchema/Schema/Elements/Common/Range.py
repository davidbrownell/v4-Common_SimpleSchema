# ----------------------------------------------------------------------
# |
# |  Range.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 07:41:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Range object"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from SimpleSchema.Schema.Elements.Common.Location import Location


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Range(object):
    """Range within a source file"""

    # ----------------------------------------------------------------------
    filename: Path
    begin: Location
    end: Location

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        filename: Path,
        begin_line: int,
        begin_column: int,
        end_line: int,
        end_column: int,
    ) -> "Range":
        return cls(
            filename,
            Location(begin_line, begin_column),
            Location(end_line, end_column),
        )

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.end < self.begin:
            raise ValueError("Invalid end")

    # ----------------------------------------------------------------------
    def ToString(
        self,
        *,
        include_filename: bool=True,
    ) -> str:
        return "{}<{} -> {}>".format(
            "{} ".format(self.filename) if include_filename else "",
            self.begin.ToString(),
            self.end.ToString(),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def Compare(
        this: "Range",
        that: "Range",
    ) -> int:
        if this.filename != that.filename:
            return -1 if this.filename < that.filename else 1

        result = Location.Compare(this.begin, that.begin)
        if result != 0:
            return result

        result = Location.Compare(this.end, that.end)
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

    # ----------------------------------------------------------------------
    def __contains__(
        self,
        location_or_range: Union[Location, "Range"],
    ) -> bool:
        if isinstance(location_or_range, Location):
            return self.begin <= location_or_range <= self.end

        if isinstance(location_or_range, Range):
            return (
                self.filename == location_or_range.filename
                and self.begin <= location_or_range.begin
                and location_or_range.end <= self.end
            )

        assert False, location_or_range  # pragma: no cover
