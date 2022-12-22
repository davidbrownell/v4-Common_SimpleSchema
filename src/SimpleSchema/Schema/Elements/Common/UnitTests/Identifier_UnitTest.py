# ----------------------------------------------------------------------
# |
# |  Identifier_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 09:35:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Identifier.py"""

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
    from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, SimpleSchemaException, SimpleElement, Visibility
    from SimpleSchema.Schema.Elements.Common.Range import Range


# ----------------------------------------------------------------------
def test_StandardType():
    filename = Path("filename")

    range1 = mock.MagicMock()
    range2 = mock.MagicMock()

    i = Identifier(
        Range.Create(filename, 1, 2, 3, 4),
        SimpleElement(range1, "The Value"),
        SimpleElement(range2, Visibility.Public),
    )
    assert i.range == Range.Create(filename, 1, 2, 3, 4)
    assert i.id.value == "The Value"
    assert i.id.range is range1

    assert i.visibility.value == Visibility.Public
    assert i.visibility.range is range2

    assert i.is_expression is False
    assert i.is_type is True

    assert Identifier(
        Range.Create(filename, 1, 2, 3, 4),
        SimpleElement(mock.MagicMock(), "_The Value"),
        SimpleElement(mock.MagicMock(), Visibility.Public),
    ).is_type


# ----------------------------------------------------------------------
def test_StandardExpression():
    filename = Path("filename")

    i = Identifier(
        Range.Create(filename, 1, 2, 3, 4),
        SimpleElement(mock.MagicMock(), "the value"),
        SimpleElement(mock.MagicMock(), mock.MagicMock()),
    )

    assert i.range == Range.Create(filename, 1, 2, 3, 4)
    assert i.id.value == "the value"

    assert i.is_expression is True
    assert i.is_type is False

    assert Identifier(
        Range.Create(filename, 1, 2, 3, 4),
        SimpleElement(mock.MagicMock(), "_the value"),
        SimpleElement(mock.MagicMock(), mock.MagicMock()),
    ).is_expression


# ----------------------------------------------------------------------
def test_Errors():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(
            Range.Create(Path("a filename"), 1, 2, 3, 4),
            SimpleElement(mock.MagicMock(), ""),
            SimpleElement(mock.MagicMock(), mock.MagicMock()),
        )

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'_' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(
            Range.Create(Path("a filename"), 1, 2, 3, 4),
            SimpleElement(mock.MagicMock(), "_"),
            SimpleElement(mock.MagicMock(), mock.MagicMock()),
        )

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'9abc' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(
            Range.Create(Path("a filename"), 1, 2, 3, 4),
            SimpleElement(mock.MagicMock(), "9abc"),
            SimpleElement(mock.MagicMock(), mock.MagicMock()),
        )

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'_9abc' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(
            Range.Create(Path("a filename"), 1, 2, 3, 4),
            SimpleElement(mock.MagicMock(), "_9abc"),
            SimpleElement(mock.MagicMock(), mock.MagicMock()),
        )
