# ----------------------------------------------------------------------
# |
# |  ParseStructureStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 10:50:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseStructureStatement.py"""

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

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseStructureStatement import ParseIdentifierType, ParseStructureStatement


# ----------------------------------------------------------------------
@pytest.mark.parametrize("has_children", [False, True])
@pytest.mark.parametrize("has_metadata", [False, True])
@pytest.mark.parametrize("has_base", [False, True])
def test_Standard(has_base, has_metadata, has_children):
    range_mock = Mock()
    name_mock = Mock()

    base_mock = [
        ParseIdentifierType(
            Mock(),
            Mock(),
            None,
            [Mock(), ],
            None,
            None,
        ),
    ] if has_base else None

    cardinality_mock = Mock()
    metadata_mock = Mock() if has_metadata else None
    children = [Mock(), Mock(), Mock()] if has_children else []

    s = ParseStructureStatement(range_mock, name_mock, base_mock, cardinality_mock, metadata_mock, children)  # type: ignore

    assert s.range is range_mock
    assert s.name is name_mock
    assert s.bases is base_mock
    assert s.cardinality is cardinality_mock
    assert s.metadata is metadata_mock
    assert s.children is children
