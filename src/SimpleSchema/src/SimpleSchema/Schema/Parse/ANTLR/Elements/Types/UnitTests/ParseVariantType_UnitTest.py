# ----------------------------------------------------------------------
# |
# |  ParseVariantType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 11:22:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseVariantType.py"""

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
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseVariantType import ParseVariantType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    types = [Mock(), Mock()]

    t = ParseVariantType(range_mock, cardinality_mock, None, types)  # type: ignore

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is None
    assert t.types is types


# ----------------------------------------------------------------------
def test_DisplayName():
    assert ParseVariantType(
        Mock(),
        Cardinality.CreateFromCode(1, 2),
        None,
        [
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name1"), ], None, None),
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(0, 1), None, [ParseIdentifier(Mock(), "Name2"), ], None, None),
        ],
    ).display_name == "_(_Name1 | _Name2?)[1, 2]"

    assert ParseVariantType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name1"), ], None, None),
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name2"), ], None, None),
            ParseIdentifierType(Mock(), Cardinality.CreateFromCode(), None, [ParseIdentifier(Mock(), "Name3"), ], None, None),
        ],
    ).display_name == "_(_Name1 | _Name2 | _Name3)"


# ----------------------------------------------------------------------
def test_ErrorNoTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Not enough types were provided. (variant_file <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseVariantType(
            Range.Create(Path("variant_file"), 1, 2, 3, 4),
            Mock(),
            None,
            [],
        )


# ----------------------------------------------------------------------
def test_ErrorSingleType():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Not enough types were provided. (variant_file <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseVariantType(
            Range.Create(Path("variant_file"), 1, 2, 3, 4),
            Mock(),
            None,
            [Mock(), ],
        )

# ----------------------------------------------------------------------
def test_ErrorNestedVariantType():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Nested variant types are not supported. (variant_file <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseVariantType(
            Mock(),
            Mock(),
            None,
            [
                Mock(),
                ParseVariantType(
                    Range.Create(Path("variant_file"), 1, 2, 3, 4),
                    Mock(),
                    None,
                    [Mock(), Mock()],
                ),
                Mock(),
            ],
        )
