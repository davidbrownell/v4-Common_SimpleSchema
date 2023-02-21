# ----------------------------------------------------------------------
# |
# |  BasicType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-17 13:34:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for BasicType.py"""

import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast, ClassVar, Tuple, Type as PythonType
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement

    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

    from SimpleSchema.Schema.Elements.Types.BasicType import BasicType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyType(BasicType):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "MyType"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (int, str, )

    value1: str                             = field(default="value1")
    value2: int                             = field(default=0)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.value1 == "throw_simple_schema_exception":
            raise SimpleSchemaException(
                Range.Create(Path("the filename"), 11, 22, 33, 44),
                "This is a sample exception.",
            )

        if self.value2 & 1:
            raise Exception("Odd values are not allowed.")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        if isinstance(value, str):
            return value + self.value1
        elif isinstance(value, int):
            if value == 12345:
                raise SimpleSchemaException(
                    Range.Create(Path("1235-file"), 1, 2, 3, 4),
                    "Error 12345",
                )

            return value + self.value2

        assert False, value  # pragma: no cover


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()

    t = MyType(range_mock)

    assert t.range is range_mock
    assert t.value1 == "value1"
    assert t.value2 == 0
    assert t.display_type == "MyType"


# ----------------------------------------------------------------------
def test_CreateFromMetadataDefault():
    range_mock = Mock()

    t = cast(MyType, MyType.CreateFromMetadata(range_mock, None))

    assert t.range is range_mock
    assert t.value1 == "value1"
    assert t.value2 == 0


# ----------------------------------------------------------------------
def test_CreateFromMetadataWithArgs():
    range_mock = Mock()

    t = cast(
        MyType,
        MyType.CreateFromMetadata(
            range_mock,
            Metadata(
                Mock(),
                [
                    MetadataItem(
                        Mock(),
                        SimpleElement[str](Mock(), "value2"),
                        IntegerExpression(Mock(), 4),
                    ),
                ],
            ),
        ),
    )

    assert t.range is range_mock
    assert t.value1 == "value1"
    assert t.value2 == 4


# ----------------------------------------------------------------------
def test_DeriveNewType():
    range_mock = Mock()

    t = MyType(range_mock, "new_value1")

    assert t.range is range_mock
    assert t.value1 == "new_value1"
    assert t.value2 == 0

    range_mock2 = Mock()

    t2 = cast(
        MyType,
        t.DeriveNewType(
            range_mock2,
            Metadata(
                Mock(),
                [
                    MetadataItem(
                        Mock(),
                        SimpleElement[str](Mock(), "value2"),
                        IntegerExpression(Mock(), 6),
                    ),
                ],
            ),
        ),
    )

    assert t2.range is range_mock2
    assert t2.value1 == "new_value1"
    assert t2.value2 == 6


# ----------------------------------------------------------------------
def test_ToPython():
    t = MyType(Mock(), "_suffix", 10)

    assert t.ToPython("foo") == "foo_suffix"
    assert t.ToPython(3) == 13


# ----------------------------------------------------------------------
def test_ErrorToPythonWrongType():
    with pytest.raises(
        Exception,
        match=re.escape("A 'float' value cannot be converted to a 'MyType' type."),
    ):
        MyType(Mock()).ToPython(3.14)

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("A 'float' value cannot be converted to a 'MyType' type. (a file here <Ln 10, Col 20 -> Ln 30, Col 40>)"),
    ):
        MyType(Mock()).ToPython(
            NumberExpression(
                Range.Create(Path("a file here"), 10, 20, 30, 40),
                3.14,
            ),
        )


# ----------------------------------------------------------------------
def test_ErrorToPythonRaiseSimpleSchemaException():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Error 12345 (1235-file <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        MyType(Mock()).ToPython(12345)

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            textwrap.dedent(
                """\
                Error 12345

                    - 1235-file <Ln 1, Col 2 -> Ln 3, Col 4>
                    - THIS_FILENAME <Ln 1, Col 2 -> Ln 3, Col 4>
                """,
            ),
        ),
    ):
        MyType(Mock()).ToPython(
            IntegerExpression(
                Range.Create(Path("THIS_FILENAME"), 1, 2, 3, 4),
                12345,
            ),
        )

# ----------------------------------------------------------------------
def test_ErrorCreateInvalidValue1():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            textwrap.dedent(
                """\
                This is a sample exception.

                    - the filename <Ln 11, Col 22 -> Ln 33, Col 44>
                    - the path here <Ln 2, Col 4 -> Ln 6, Col 8>
                """,
            ),
        ),
    ):
        MyType.CreateFromMetadata(
            Mock(),
            Metadata(
                Range.Create(Path("the path here"), 2, 4, 6, 8),
                [
                    MetadataItem(
                        Mock(),
                        SimpleElement[str](Mock(), "value1"),
                        StringExpression(
                            Mock(),
                            "throw_simple_schema_exception",
                        ),
                    ),
                ],
            ),
        )


# ----------------------------------------------------------------------
def test_ErrorCreateInvalidValue2():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Odd values are not allowed. (the path here <Ln 1, Col 3 -> Ln 5, Col 7>)"),
    ):
        MyType.CreateFromMetadata(
            Mock(),
            Metadata(
                Range.Create(Path("the path here"), 1, 3, 5, 7),
                [
                    MetadataItem(
                        Mock(),
                        SimpleElement[str](Mock(), "value2"),
                        IntegerExpression(Mock(), 3),
                    ),
                ],
            ),
        )
