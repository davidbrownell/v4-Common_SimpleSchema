# ----------------------------------------------------------------------
# |
# |  ParseTupleType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:16:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseTupleType.py"""

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
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Parse.ParseElements.Types.ParseTupleType import ParseTupleType, ParseType


# ----------------------------------------------------------------------
def test_Standard():
    i1 = ParseType(mock.MagicMock(), mock.MagicMock(), mock.MagicMock())
    i2 = ParseType(mock.MagicMock(), mock.MagicMock(), mock.MagicMock())

    cardinality = mock.MagicMock()
    metadata = mock.MagicMock()

    t = ParseTupleType(
        Range.Create(Path("tuple_file"), 1, 1, 3, 1),
        cardinality,
        metadata,
        [i1],
    )

    assert t.range == Range.Create(Path("tuple_file"), 1, 1, 3, 1)
    assert t.cardinality is cardinality
    assert t.metadata is metadata
    assert t.types == [i1]

    t = ParseTupleType(
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
        [i1, i2],
    )

    assert t.types == [i1, i2]


# ----------------------------------------------------------------------
def test_ErrorEmpty():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No types were provided. (file <[1, 2] -> [3, 4]>)"),
    ):
        ParseTupleType(
            Range.Create(Path("file"), 1, 2, 3, 4),
            mock.MagicMock(),
            mock.MagicMock(),
            [],
        )
