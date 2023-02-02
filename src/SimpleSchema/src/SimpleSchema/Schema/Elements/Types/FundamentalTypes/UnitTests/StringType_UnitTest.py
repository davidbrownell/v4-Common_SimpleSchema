# ----------------------------------------------------------------------
# |
# |  StringType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 14:58:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for StringType.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality

    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.StringType import StringType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    metadata_mock = Mock()

    s = StringType(range_mock, Cardinality.CreateFromCode(), metadata_mock)

    assert s.range is range_mock
    assert s.cardinality.is_single
    assert s.metadata is metadata_mock
    assert s.min_length == 1
    assert s.max_length is None
    assert s.validation_expression is None

    assert s.ToPython(StringExpression(Mock(), "foo")) == "foo"


# ----------------------------------------------------------------------
def test_DisplayName():
    assert StringType(Mock(), Cardinality.CreateFromCode(0, 1), None).display_name == "String?"
    assert StringType(Mock(), Cardinality.CreateFromCode(0, 1), None, min_length=0).display_name == "String (>= no characters)?"
    assert StringType(Mock(), Cardinality.CreateFromCode(0, 1), None, max_length=10).display_name == "String (<= 10 characters)?"
    assert StringType(Mock(), Cardinality.CreateFromCode(0, 1), None, validation_expression="foo").display_name == "String ('foo')?"
    assert StringType(Mock(), Cardinality.CreateFromCode(0, 1), None, 2, 10, 'does not make sense').display_name == "String (>= 2 characters, <= 10 characters, 'does not make sense')?"



# ----------------------------------------------------------------------
def test_Clone():
    st = StringType(Mock(), Mock(), None)

    assert st.Clone() == st


# ----------------------------------------------------------------------
def test_ErrorInvalidMin():
    with pytest.raises(
        Exception,
        match=re.escape("-1 < 0"),
    ):
        StringType(Mock(), Mock(), None, -1)


# ----------------------------------------------------------------------
def test_ErrorInvalidMax():
    with pytest.raises(
        Exception,
        match=re.escape("10 > 1"),
    ):
        StringType(Mock(), Mock(), None, 10, 1)


# ----------------------------------------------------------------------
def test_ErrorValidateMin():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("At least 2 characters were expected (1 character was found). (a file <Ln 10, Col 20 -> Ln 30, Col 40>)"),
    ):
        s = StringType(Mock(), Cardinality.CreateFromCode(), None, 2)

        assert s.ToPython(StringExpression(Mock(), "123")) == "123"
        assert s.ToPython(StringExpression(Mock(), "12")) == "12"

        s.ToPython(StringExpression(Range.Create(Path("a file"), 10, 20, 30, 40), "1"))


# ----------------------------------------------------------------------
def test_ErrorValidateMax():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No more than 3 characters were expected (4 characters were found). (a file <Ln 10, Col 20 -> Ln 30, Col 40>)"),
    ):
        s = StringType(Mock(), Cardinality.CreateFromCode(), None, max_length=3)

        assert s.ToPython(StringExpression(Mock(), "12")) == "12"
        assert s.ToPython(StringExpression(Mock(), "123")) == "123"

        s.ToPython(StringExpression(Range.Create(Path("a file"), 10, 20, 30, 40), "1234"))


# ----------------------------------------------------------------------
def test_ErrorValidateExpression():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("The value 'bar' does not match the regular expression 'foo'. (a file <Ln 10, Col 20 -> Ln 30, Col 40>)"),
    ):
        s = StringType(Mock(), Cardinality.CreateFromCode(), None, validation_expression="foo")

        assert s.ToPython(StringExpression(Mock(), "foo")) == "foo"

        s.ToPython(StringExpression(Range.Create(Path("a file"), 10, 20, 30, 40), "bar"))
