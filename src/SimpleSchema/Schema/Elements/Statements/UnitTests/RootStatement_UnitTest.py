# ----------------------------------------------------------------------
# |
# |  RootStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:14:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for RootStatement.py"""

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
    from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, SimpleElement
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement

    from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
def test_Empty():
    range = mock.MagicMock()

    r = RootStatement(range, [])

    assert r.range is range
    assert r.statements == []


# ----------------------------------------------------------------------
def test_WithStatements():
    range1 = mock.MagicMock()

    s1 = ItemStatement(
        mock.MagicMock(),
        Identifier(
            mock.MagicMock(),
            SimpleElement(range1, "foo"),
            SimpleElement(mock.MagicMock(), mock.MagicMock()),
        ),
        Type(mock.MagicMock(), mock.MagicMock(), None),
    )

    r = RootStatement(range1, [s1, s1])

    assert r.range is range1
    assert r.statements == [s1, s1]


# ----------------------------------------------------------------------
def test_ErrorNestedRoot():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Root statements may not contain nested root statements. (invalid_root <[10, 20] -> [30, 40]>)"),
    ):
        RootStatement(
            mock.MagicMock(),
            [
                RootStatement(Range.Create(Path("invalid_root"), 10, 20, 30, 40), []),
            ],
        )
