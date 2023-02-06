# ----------------------------------------------------------------------
# |
# |  EnumType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 08:07:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for EnumType.py"""

import re
import sys

from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.EnumType import EnumType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    et = EnumType(range_mock, cardinality_mock, metadata_mock, [1, 2, 3])

    assert et.NAME == "Enum"
    assert et.SUPPORTED_PYTHON_TYPES == (Enum, str, int, )

    assert et.range is range_mock
    assert et.cardinality is cardinality_mock
    assert et.metadata is metadata_mock

    assert [(e.name, e.value) for e in et.EnumClass] == [
        ("Value1", 1),
        ("Value2", 2),
        ("Value3", 3),
    ]


# ----------------------------------------------------------------------
def test_CreateFromExisting():
    et = EnumType(Mock(), Mock(), None, [1, 2, 3])

    range_mock = Mock()
    cardinality = Cardinality.CreateFromCode()
    metadata_mock = Mock()

    et2 = EnumType(range_mock, cardinality, metadata_mock, [], 0, et.EnumClass)

    assert et2.range is range_mock
    assert et2.cardinality is cardinality
    assert et2.metadata is metadata_mock
    assert et2.EnumClass is et.EnumClass


# ----------------------------------------------------------------------
def test_DisplayName():
    assert EnumType(Mock(), Cardinality.CreateFromCode(), None, [1, 2, 3]).display_name == "Enum"


# ----------------------------------------------------------------------
def test_Clone():
    et = EnumType(Mock(), Mock(), None, [1, 2, 3])

    et2 = et.Clone(Mock(), Mock())

    assert et2.EnumClass is et.EnumClass


# ----------------------------------------------------------------------
def test_ToPython():
    et = EnumType(Mock(), Cardinality.CreateFromCode(), None, [1, 2, 3])

    assert et.ToPython(et.EnumClass.Value1) == et.EnumClass.Value1
    assert et.ToPython("Value2") == et.EnumClass.Value2
    assert et.ToPython(3) == et.EnumClass.Value3


# ----------------------------------------------------------------------
def test_EnumStrings():
    et = EnumType(Mock(), Cardinality.CreateFromCode(), None, ["One", "Two", "Three"])

    assert et.ToPython(et.EnumClass.One) == et.EnumClass.One
    assert et.ToPython("Two") == et.EnumClass.Two
    assert et.ToPython(3) == et.EnumClass.Three


# ----------------------------------------------------------------------
def test_IntTuples():
    et = EnumType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [
            (1, "OneValue"),
            (2, "TwoValue"),
            (3, "ThreeValue"),
        ],
    )

    assert et.ToPython(et.EnumClass.Value1) == et.EnumClass.Value1
    assert et.ToPython("TwoValue") == et.EnumClass.Value2
    assert et.ToPython(3) == et.EnumClass.Value3


# ----------------------------------------------------------------------
def test_StringTuples():
    et = EnumType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [
            ("One", "OneValue"),
            ("Two", "TwoValue"),
            ("Three", "ThreeValue"),
        ],
    )

    assert et.ToPython(et.EnumClass.One) == et.EnumClass.One
    assert et.ToPython("TwoValue") == et.EnumClass.Two
    assert et.ToPython("Three") == et.EnumClass.Three


# ----------------------------------------------------------------------
def test_StartingValue():
    et = EnumType(Mock(), Cardinality.CreateFromCode(), None, [1, 2, 3], starting_value=101)

    assert et.ToPython(et.EnumClass.Value1) == et.EnumClass.Value1
    assert et.ToPython(102) == et.EnumClass.Value2
    assert et.ToPython("Value3").value == 103


# ----------------------------------------------------------------------
def test_ErrorNoValues():
    with pytest.raises(
        ValueError,
        match=re.escape("Values must be provided."),
    ):
        EnumType(Mock(), Mock(), None, [])


# ----------------------------------------------------------------------
def test_ErrorInvalidValue():
    with pytest.raises(
        ValueError,
        match=re.escape("An Integer or String value was expected."),
    ):
        EnumType(Mock(), Mock(), None, [1.1, 2, 3])


# ----------------------------------------------------------------------
def test_ErrorStringWithIntValues():
    with pytest.raises(
        ValueError,
        match=re.escape("An Integer was expected (index: 2)."),
    ):
        EnumType(Mock(), Mock(), None, [1, 2, "3"])


# ----------------------------------------------------------------------
def test_ErrorIntWithStringValues():
    with pytest.raises(
        ValueError,
        match=re.escape("A String was expected (index: 1)."),
    ):
        EnumType(Mock(), Mock(), None, ["1", 2, "3"])


# ----------------------------------------------------------------------
def test_ErrorTuplesWithRawValues():
    with pytest.raises(
        ValueError,
        match=re.escape("A tuple was not expected (index: 2)."),
    ):
        EnumType(Mock(), Mock(), None, [1, 2, (3, "Three")])


# ----------------------------------------------------------------------
def test_ErrorRawValueWithTuples():
    with pytest.raises(
        ValueError,
        match=re.escape("A tuple was expected (index: 1)."),
    ):
        EnumType(Mock(), Mock(), None, [(1, "one"), 2, (3, "three")])


# ----------------------------------------------------------------------
def test_ErrorTupleStringWithTupleInts():
    with pytest.raises(
        ValueError,
        match=re.escape("An Integer was expected (index: 1)."),
    ):
        EnumType(Mock(), Mock(), None, [(1, "one"), ("2", "two")])


# ----------------------------------------------------------------------
def test_ErrorTupleIntWithTupleStrings():
    with pytest.raises(
        ValueError,
        match=re.escape("A String was expected (index: 1)."),
    ):
        EnumType(Mock(), Mock(), None, [("1", "one"), (2, "two")])


# ----------------------------------------------------------------------
def test_ErrorNonStringDescInTuple():
    with pytest.raises(
        ValueError,
        match=re.escape("A string value is required."),
    ):
        EnumType(Mock(), Mock(), None, [(1, "1"), (2, "")])


# ----------------------------------------------------------------------
def test_ErrorUnrecognizedValue():
    with pytest.raises(
        Exception,
        match=re.escape("'not valid' is not a valid enum value."),
    ):
        EnumType(Mock(), Mock(), None, [1, 2, 3]).ToPython("not valid")
