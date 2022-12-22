# ----------------------------------------------------------------------
# |
# |  Range_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 09:37:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Range.py"""

import re
import sys

from pathlib import Path

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range, Location


# ----------------------------------------------------------------------
def test_Standard():
    r = Range(Path("the filename"), Location(1, 2), Location(3, 4))

    assert r.filename == Path("the filename")
    assert r.begin == Location(1, 2)
    assert r.end == Location(3, 4)


# ----------------------------------------------------------------------
def test_Create():
    r = Range.Create(Path("another filename"), 1, 2, 3, 4)

    assert r.filename == Path("another filename")
    assert r.begin == Location(1, 2)
    assert r.end == Location(3, 4)


# ----------------------------------------------------------------------
def test_ToString():
    assert Range.Create(Path("filename"), 1, 2, 3, 4).ToString() == "filename <[1, 2] -> [3, 4]>"
    assert Range.Create(Path("filename"), 1, 2, 3, 4).ToString(include_filename=False) == "<[1, 2] -> [3, 4]>"


# ----------------------------------------------------------------------
def test_Invalid():
    with pytest.raises(
        ValueError,
        match=re.escape("Invalid end"),
    ):
        Range.Create(Path("filename"), 10, 20, 2, 3)


# ----------------------------------------------------------------------
def test_Compare():
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) == 0

    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file___"), 10, 20, 30, 40)) != 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 1, 20, 30, 40)) != 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 2, 30, 40)) != 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 25, 40)) != 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 4)) != 0

    assert Range.Compare(Range.Create(Path("AAAA"), 10, 20, 30, 40), Range.Create(Path("ZZZZ"), 10, 20, 30, 40)) < 0
    assert Range.Compare(Range.Create(Path("file"), 1, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) < 0
    assert Range.Compare(Range.Create(Path("file"), 10, 2, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) < 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 25, 40), Range.Create(Path("file"), 10, 20, 30, 40)) < 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 4), Range.Create(Path("file"), 10, 20, 30, 40)) < 0

    assert Range.Compare(Range.Create(Path("AAAA"), 10, 20, 30, 40), Range.Create(Path("ZZZZ"), 10, 20, 30, 40)) <= 0
    assert Range.Compare(Range.Create(Path("file"), 1, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) <= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 2, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) <= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 25, 40), Range.Create(Path("file"), 10, 20, 30, 40)) <= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 4), Range.Create(Path("file"), 10, 20, 30, 40)) <= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) <= 0

    assert Range.Compare(Range.Create(Path("ZZZZ"), 10, 20, 30, 40), Range.Create(Path("AAAA"), 10, 20, 30, 40)) > 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 1, 20, 30, 40)) > 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 2, 30, 40)) > 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 25, 40)) > 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 4)) > 0

    assert Range.Compare(Range.Create(Path("ZZZZ"), 10, 20, 30, 40), Range.Create(Path("AAAA"), 10, 20, 30, 40)) >= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 1, 20, 30, 40)) >= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 2, 30, 40)) >= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 25, 40)) >= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 4)) >= 0
    assert Range.Compare(Range.Create(Path("file"), 10, 20, 30, 40), Range.Create(Path("file"), 10, 20, 30, 40)) == 0


# ----------------------------------------------------------------------
def test_ComparisonOperators():
    assert Range.Create(Path("file"), 10, 20, 30, 40) == Range(Path("file"), Location(10, 20), Location(30, 40))

    assert Range.Create(Path("file"), 10, 20, 30, 40) != Range(Path("file___"), Location(10, 20), Location(30, 40))

    assert Range.Create(Path("file"), 10, 2, 30, 40) < Range(Path("file"), Location(10, 20), Location(30, 40))

    assert Range.Create(Path("file"), 10, 2, 30, 40) <= Range(Path("file"), Location(10, 20), Location(30, 40))
    assert Range.Create(Path("file"), 10, 20, 30, 40) <= Range(Path("file"), Location(10, 20), Location(30, 40))

    assert Range.Create(Path("file"), 10, 20, 31, 40) > Range(Path("file"), Location(10, 20), Location(30, 40))

    assert Range.Create(Path("file"), 10, 20, 31, 40) >= Range(Path("file"), Location(10, 20), Location(30, 40))
    assert Range.Create(Path("file"), 10, 20, 30, 40) >= Range(Path("file"), Location(10, 20), Location(30, 40))


# ----------------------------------------------------------------------
class TestContains(object):
    # ----------------------------------------------------------------------
    def test_Location(self):
        the_range = Range.Create(Path("filename"), 10, 20, 30, 40)

        assert Location(10, 20) in the_range
        assert Location(30, 40) in the_range
        assert Location(10, 25) in the_range
        assert Location(22, 1) in the_range

        assert Location(10, 1) not in the_range
        assert Location(1, 1) not in the_range
        assert Location(30, 41) not in the_range
        assert Location(40, 1) not in the_range

    # ----------------------------------------------------------------------
    def test_Range(self):
        the_range = Range.Create(Path("filename"), 10, 20, 30, 40)

        assert Range.Create(Path("filename"), 10, 20, 30, 40) in the_range
        assert Range.Create(Path("filename"), 11, 20, 30, 40) in the_range
        assert Range.Create(Path("filename"), 10, 20, 29, 40) in the_range
        assert Range.Create(Path("filename"), 10, 21, 30, 40) in the_range
        assert Range.Create(Path("filename"), 10, 20, 30, 22) in the_range
        assert Range.Create(Path("filename"), 15, 1, 20, 1) in the_range

        assert Range.Create(Path("filename___"), 10, 20, 30, 40) not in the_range
        assert Range.Create(Path("filename"), 1, 20, 30, 40) not in the_range
        assert Range.Create(Path("filename"), 1, 20, 7, 40) not in the_range
        assert Range.Create(Path("filename"), 1, 20, 35, 40) not in the_range

        assert Range.Create(Path("filename"), 10, 20, 50, 40) not in the_range
        assert Range.Create(Path("filename"), 15, 20, 50, 40) not in the_range
        assert Range.Create(Path("filename"), 50, 20, 60, 40) not in the_range
