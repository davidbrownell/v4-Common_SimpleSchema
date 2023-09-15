# ----------------------------------------------------------------------
# |
# |  ParseTupleType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 11:02:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseTupleType.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifier, ParseIdentifierType
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseTupleType import ParseTupleType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    types_mock = Mock()

    t = ParseTupleType(range_mock, cardinality_mock, None, types_mock)

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.unresolved_metadata is None
    assert t.types is types_mock


# ----------------------------------------------------------------------
def test_DisplayType():
    assert ParseTupleType(
        Mock(),
        Cardinality.CreateFromCode(0, 1),
        None,
        [
            ParseIdentifierType(
                Mock(),
                Cardinality.CreateFromCode(2, 2),
                None,
                [ParseIdentifier(Mock(), "Name"), ],
                None,
            ),
        ],
    ).display_type == "(Name[2], )?"

    assert ParseTupleType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name1"), ], None),
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name2"), ], None),
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name3"), ], None),
        ],
    ).display_type == "(Name1, Name2, Name3, )"


# ----------------------------------------------------------------------
def test_ErrorNoTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No tuple types were provided. (tuple_file <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseTupleType(
            Range.Create(Path("tuple_file"), 1, 2, 3, 4),
            Mock(),
            None,
            [],
        )
