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

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Identifier import Identifier, SimpleSchemaException
    from SimpleSchema.Schema.Impl.Common.Range import Range


# ----------------------------------------------------------------------
def test_StandardType():
    filename = Path("filename")

    i = Identifier(Range.Create(filename, 1, 2, 3, 4), "The Value")
    assert i.range == Range.Create(filename, 1, 2, 3, 4)
    assert i.value == "The Value"

    assert i.is_expression is False
    assert i.is_type is True

    assert Identifier(Range.Create(filename, 1, 2, 3, 4), "_The Value").is_type


# ----------------------------------------------------------------------
def test_StandardExpression():
    filename = Path("filename")

    i = Identifier(Range.Create(filename, 1, 2, 3, 4), "the value")
    assert i.range == Range.Create(filename, 1, 2, 3, 4)
    assert i.value == "the value"

    assert i.is_expression is True
    assert i.is_type is False

    assert Identifier(Range.Create(filename, 1, 2, 3, 4), "_the value").is_expression


# ----------------------------------------------------------------------
def test_Errors():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(Range.Create(Path("a filename"), 1, 2, 3, 4), "")

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'_' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(Range.Create(Path("a filename"), 1, 2, 3, 4), "_")

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'9abc' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(Range.Create(Path("a filename"), 1, 2, 3, 4), "9abc")

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'_9abc' is not a valid identifier. (a filename <[1, 2] -> [3, 4]>)"),
    ):
        Identifier(Range.Create(Path("a filename"), 1, 2, 3, 4), "_9abc")
