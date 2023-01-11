# ----------------------------------------------------------------------
# |
# |  Cardinality_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 12:01:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Cardinality.py"""

import re
import sys

from pathlib import Path
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import *
    from SimpleSchema.Schema.Elements.Common.Range import Range


# ----------------------------------------------------------------------
def test_Single():
    r = Range.Create(Path("the file"), 1, 2, 3, 4)

    c = Cardinality(r, None, None, None)

    assert c.range is r

    assert c.min.value == 1
    assert c.min.range is r

    assert c.max is not None
    assert c.max.value == 1
    assert c.max.range is r

    assert c.is_single
    assert c.is_optional is False

    assert c.metadata is None


# ----------------------------------------------------------------------
def test_MaxNoMin():
    r = Range.Create(Path("the file"), 1, 2, 3, 4)

    c = Cardinality(r, None, IntegerExpression(Range.Create(Path("the file 2"), 10, 20, 30, 40), 10), None)

    assert c.range is r

    assert c.min.value == 0
    assert c.min.range is r

    assert c.max is not None
    assert c.max.value == 10
    assert c.max.range.filename == Path("the file 2")

    assert c.is_single is False
    assert c.is_optional is False

    assert c.metadata is None


# ----------------------------------------------------------------------
def test_Range():
    r1 = Range.Create(Path("file1"), 1, 2, 3, 4)
    r2 = Range.Create(Path("file2"), 10, 20, 30, 40)
    r3 = Range.Create(Path("file3"), 11, 21, 31, 41)

    c = Cardinality(r1, IntegerExpression(r2, 10), IntegerExpression(r3, 20), None)

    assert c.range is r1

    assert c.min.value == 10
    assert c.min.range is r2

    assert c.max is not None
    assert c.max.value == 20
    assert c.max.range is r3

    assert c.is_single is False
    assert c.is_optional is False

    assert c.metadata is None


# ----------------------------------------------------------------------
def test_ZeroOrMore():
    r1 = Range.Create(Path("file1"), 1, 2, 3, 4)
    r2 = Range.Create(Path("file2"), 5, 6, 7, 8)

    c = Cardinality(r1, IntegerExpression(r2, 0), None, None)

    assert c.range is r1

    assert c.min.range is r2
    assert c.min.value == 0

    assert c.max is None

    assert c.is_single is False
    assert c.is_optional is False

    assert c.metadata is None


# ----------------------------------------------------------------------
def test_OneOrMore():
    r1 = Range.Create(Path("file1"), 1, 2, 3, 4)
    r2 = Range.Create(Path("file2"), 5, 6, 7, 8)

    c = Cardinality(r1, IntegerExpression(r2, 1), None, None)

    assert c.range is r1

    assert c.min.range is r2
    assert c.min.value == 1

    assert c.max is None

    assert c.is_single is False
    assert c.is_optional is False

    assert c.metadata is None


# ----------------------------------------------------------------------
def test_WithMetadata():
    the_range = mock.MagicMock()
    the_metadata = mock.MagicMock()

    c = Cardinality(the_range, IntegerExpression(mock.MagicMock(), 2), None, the_metadata)

    assert c.range is the_range
    assert c.metadata is the_metadata


# ----------------------------------------------------------------------
def test_ErrorInvalidRange():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Invalid cardinality (20 > 12). (file2 <[10, 20] -> [30, 40]>)"),
    ):
        Cardinality(
            Range.Create(Path("file"), 1, 2, 3, 4),
            IntegerExpression(mock.MagicMock(), 20),
            IntegerExpression(Range.Create(Path("file2"), 10, 20, 30, 40), 12),
            None,
        )


# ----------------------------------------------------------------------
def test_ErrorMetadata():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Metadata cannot be associated with single elements. (invalid file <[10, 20] -> [30, 40]>)"),
    ):
        Cardinality(
            mock.MagicMock(),
            None,
            None,
            Metadata(
                Range.Create(Path("invalid file"), 10, 20, 30, 40),
                [
                    mock.MagicMock(),
                ],
            ),
        )
