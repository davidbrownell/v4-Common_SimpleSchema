# ----------------------------------------------------------------------
# |
# |  ParseIdentifier_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:37:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseIdentifier.py"""

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
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Common.ParseIdentifier import ParseIdentifier, SimpleElement, Visibility


# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    "value",
    [
        # Types
        ("Hello!", Visibility.Public, False, True),
        ("__Hello!", Visibility.Private, True, True),
        ("@Hello!",Visibility.Protected, True, True),

        # Expressions
        ("hello!", Visibility.Public, False, False),
        ("__hello!", Visibility.Private, True, False),
        ("@hello!",Visibility.Protected, True, False),
    ],
)
def test_Standard(value):
    value, visibility, is_visibility_range_new, is_type = value

    range_value = Range.Create(Path(__file__), 1, 1, 2, 1)

    id = ParseIdentifier(range_value, value)

    assert id.range is range_value
    assert id.value == value
    assert id.visibility.value is visibility

    if is_visibility_range_new:
        assert id.visibility.range == Range.Create(
            range_value.filename,
            range_value.begin.line,
            range_value.begin.column,
            range_value.begin.line,
            range_value.begin.column + 1,
        )
    else:
        assert id.visibility.range is id.range

    assert id.is_expression != is_type
    assert id.is_type == is_type


# ----------------------------------------------------------------------
def test_ToSimpleElement():
    id = ParseIdentifier(Mock(), "Value")

    se = id.ToSimpleElement()

    assert se.range is id.range
    assert se.value == "Value"


# ----------------------------------------------------------------------
@pytest.mark.parametrize("value", ["", "_", "____"])
def test_ErrorNoMeaningful(value):
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'{}' does not have any identifiable characters. (a__file <Ln 1, Col 2 -> Ln 3, Col 4>)".format(value)),
    ):
        ParseIdentifier(Range.Create(Path("a__file"), 1, 2, 3, 4), value)


# ----------------------------------------------------------------------
@pytest.mark.parametrize("value", ["7value", "_1value", "<value"])
def test_ErrorNotAlpha(value):
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("The first identifiable character in '{}' must be a letter. (a__file <Ln 1, Col 2 -> Ln 3, Col 4>)".format(value)),
    ):
        ParseIdentifier(Range.Create(Path("a__file"), 1, 2, 3, 4), value)
