# ----------------------------------------------------------------------
# |
# |  ParseIdentifierType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:57:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseIdentifierType.py"""

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


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()
    identifiers_mock = Mock()
    is_global_reference_mock = Mock()
    is_item_reference_mock = Mock()

    pit = ParseIdentifierType(
        range_mock,
        cardinality_mock,
        metadata_mock,
        identifiers_mock,
        is_global_reference_mock,
        is_item_reference_mock,
    )

    assert pit.range is range_mock
    assert pit.cardinality is cardinality_mock
    assert pit.metadata is metadata_mock
    assert pit.identifiers is identifiers_mock
    assert pit.is_global_reference is is_global_reference_mock
    assert pit.is_item_reference is is_item_reference_mock


# ----------------------------------------------------------------------
def test_DisplayNameSingle():
    assert ParseIdentifierType(
        Mock(),
        Cardinality.CreateFromCode(2, 2),
        None,
        [
            ParseIdentifier(Mock(), "Name"),
        ],
        None,
        None,
    ).display_name == "_Name[2]"

    assert ParseIdentifierType(
        Mock(),
        Cardinality.CreateFromCode(0, 1),
        None,
        [
            ParseIdentifier(Mock(), "Name"),
        ],
        Mock(),
        None,
    ).display_name == "_::Name?"

    assert ParseIdentifierType(
        Mock(),
        Cardinality.CreateFromCode(1),
        None,
        [
            ParseIdentifier(Mock(), "Name"),
        ],
        None,
        Mock(),
    ).display_name == "_Name::item+"

    assert ParseIdentifierType(
        Mock(),
        Cardinality.CreateFromCode(1, 2),
        None,
        [
            ParseIdentifier(Mock(), "Name"),
        ],
        Mock(),
        Mock(),
    ).display_name == "_::Name::item[1, 2]"


# ----------------------------------------------------------------------
def test_DisplayNameMultiple():
    assert ParseIdentifierType(
        Mock(),
        Cardinality.CreateFromCode(0, 1),
        None,
        [
            ParseIdentifier(Mock(), "Name1"),
            ParseIdentifier(Mock(), "Name2"),
            ParseIdentifier(Mock(), "Name3"),
        ],
        None,
        None,
    ).display_name == "_Name1.Name2.Name3?"

    assert ParseIdentifierType(
        Mock(),
        Cardinality.CreateFromCode(2),
        None,
        [
            ParseIdentifier(Mock(), "Name1"),
            ParseIdentifier(Mock(), "Name2"),
            ParseIdentifier(Mock(), "Name3"),
        ],
        None,
        Mock(),
    ).display_name == "_Name1.Name2.Name3::item[2+]"


# ----------------------------------------------------------------------
def test_ErrorEmpty():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Identifier types must have at least one identifier. (a f_i_l_e <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseIdentifierType(
            Range.Create(Path("a f_i_l_e"), 1, 2, 3, 4),
            Mock(),
            None,
            [],
            None,
            None,
        )


# ----------------------------------------------------------------------
def test_ErrorNotAType():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'name2' is not a valid type name. (a f_i_l_e <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseIdentifierType(
            Mock(),
            Mock(),
            None,
            [
                ParseIdentifier(Mock(), "Name1"),
                ParseIdentifier(Range.Create(Path("a f_i_l_e"), 1, 2, 3, 4), "name2"),
            ],
            None,
            None,
        )


# ----------------------------------------------------------------------
def test_ErrorInvalidGlobal():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("There may only be one identifier for global types. (a f_i_l_e <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        ParseIdentifierType(
            Mock(),
            Mock(),
            None,
            [
                ParseIdentifier(Mock(), "Name1"),
                ParseIdentifier(Mock(), "Name2"),
            ],
            Range.Create(Path("a f_i_l_e"), 1, 2, 3, 4),
            None,
        )
