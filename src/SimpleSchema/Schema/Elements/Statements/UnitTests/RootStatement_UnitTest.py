# ----------------------------------------------------------------------
# |
# |  RootStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 14:15:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for RootStatement.py"""

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
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    statements_mock = Mock()

    r = RootStatement(range_mock, statements_mock)

    assert r.range is range_mock
    assert r.statements is statements_mock
    assert r.CHILDREN_NAME == "statements"
    assert r.parent is None


# ----------------------------------------------------------------------
def test_ErrorSetParent():
    with pytest.raises(
        Exception,
        match=re.escape("Root statements cannot have parents."),
    ):
        RootStatement(Mock(), Mock()).SetParent(Mock())


# ----------------------------------------------------------------------
def test_ErrorNested():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Root statements may not be nested. (FILE <Ln 100, Col 200 -> Ln 300, Col 400>)"),
    ):
        RootStatement(
            Mock(),
            [
                Mock(),
                RootStatement(
                    Range.Create(Path("FILE"), 100, 200, 300, 400),
                    [],
                ),
                Mock(),
            ],
        )
