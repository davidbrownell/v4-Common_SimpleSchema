# ----------------------------------------------------------------------
# |
# |  StructureStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 10:29:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for StructureStatement.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement
    from SimpleSchema.Schema.Elements.Types.TupleType import TupleType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    visibility_mock = Mock()
    name_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    ss = StructureStatement(range_mock, visibility_mock, name_mock, [], cardinality_mock, metadata_mock, [])

    assert ss.range is range_mock
    assert ss.visibility is visibility_mock
    assert ss.name is name_mock
    assert ss.base_types == []
    assert ss.cardinality is cardinality_mock
    assert ss.metadata is metadata_mock
    assert ss.children == []


# ----------------------------------------------------------------------
def test_ErrorInvalidSingleType():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Base classes must be fundamental or structure types when a single base class is specified. (filename <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        invalid_type = Mock()
        invalid_type.range = Range.Create(Path("filename"), 1, 2, 3, 4)

        StructureStatement(
            Mock(),
            Mock(),
            Mock(),
            [
                invalid_type,
            ],
            Mock(),
            None,
            [],
        )


# ----------------------------------------------------------------------
def test_ErrorInvalidMultipleTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Base classes must be structure types when multiple base classes are specified. (filename <Ln 10, Col 20 -> Ln 30, Col 40>)"),
    ):
        invalid_type = Mock()
        invalid_type.range = Range.Create(Path("filename"), 10, 20, 30, 40)

        StructureStatement(
            Mock(),
            Mock(),
            Mock(),
            [
                invalid_type,
                Mock(),
            ],
            Mock(),
            None,
            [],
        )
