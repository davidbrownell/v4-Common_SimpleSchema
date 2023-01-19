# ----------------------------------------------------------------------
# |
# |  Location_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 20:10:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Location.py"""

import re
import sys

from pathlib import Path

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Location import Location


# ----------------------------------------------------------------------
def test_Standard():
    l = Location(10, 11)
    assert l.line == 10
    assert l.column == 11


# ----------------------------------------------------------------------
def test_InvalidLocation():
    with pytest.raises(
        ValueError,
        match=re.escape("Invalid line"),
    ):
        Location(0, 2)

    with pytest.raises(
        ValueError,
        match=re.escape("Invalid column"),
    ):
        Location(1, 0)


# ----------------------------------------------------------------------
def test_String():
    assert str(Location(1, 2)) == "Ln 1, Col 2"


# ----------------------------------------------------------------------
def test_Compare():
    assert Location.Compare(Location(1, 2), Location(1, 2)) == 0

    assert Location.Compare(Location(1, 2), Location(3, 4)) != 0
    assert Location.Compare(Location(1, 2), Location(1, 4)) != 0

    assert Location.Compare(Location(1, 2), Location(3, 4)) < 0
    assert Location.Compare(Location(1, 2), Location(1, 3)) < 0

    assert Location.Compare(Location(1, 2), Location(3, 4)) <= 0
    assert Location.Compare(Location(1, 2), Location(1, 3)) <= 0
    assert Location.Compare(Location(1, 2), Location(1, 2)) <= 0

    assert Location.Compare(Location(3, 4), Location(1, 2)) > 0
    assert Location.Compare(Location(3, 4), Location(3, 1)) > 0

    assert Location.Compare(Location(3, 4), Location(1, 2)) >= 0
    assert Location.Compare(Location(3, 4), Location(3, 1)) >= 0
    assert Location.Compare(Location(3, 4), Location(3, 4)) >= 0


# ----------------------------------------------------------------------
def test_ComparisonOperators():
    assert Location(1, 2) == Location(1, 2)

    assert Location(1, 2) != Location(3, 4)
    assert Location(1, 2) != Location(1, 4)

    assert Location(1, 2) < Location(3, 4)
    assert Location(1, 2) < Location(1, 3)

    assert Location(1, 2) <= Location(3, 4)
    assert Location(1, 2) <= Location(1, 3)
    assert Location(1, 2) <= Location(1, 2)

    assert Location(3, 4) > Location(1, 2)
    assert Location(3, 4) > Location(3, 1)

    assert Location(3, 4) >= Location(1, 2)
    assert Location(3, 4) >= Location(3, 1)
    assert Location(3, 4) >= Location(3, 4)
