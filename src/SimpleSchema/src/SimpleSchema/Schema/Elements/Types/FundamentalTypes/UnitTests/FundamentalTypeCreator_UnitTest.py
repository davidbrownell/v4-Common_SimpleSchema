# ----------------------------------------------------------------------
# |
# |  FundamentalTypeCreator_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 07:22:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for FundamentalTypeCreator.py"""

import re
import sys

from dataclasses import dataclass, field
from enum import auto, Enum
from pathlib import Path
from typing import ClassVar, Optional, Tuple, Type as PythonType, Union
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement

    from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
    from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
    from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
    from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

    from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.FundamentalTypeCreator import CreateFromMetadata


# ----------------------------------------------------------------------
# |
# |  Public TYpes
# |
# ----------------------------------------------------------------------
class MyEnum(Enum):
    One                                     = auto()
    Two                                     = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyType(FundamentalType):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "MyType"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    a: int
    b: int                                  = field(default=10)
    c: Optional[int]                        = field(default=None)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "MyType":
        return MyType(range_value, cardinality, metadata, self.a, self.b, self.c)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ComplexType(FundamentalType):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Complex"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    b: bool
    e: MyEnum
    f: float
    i: int
    s: str

    optional: Optional[bool]
    variant: Union[bool, int]

    l: list[bool]
    t: Tuple[int, str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        raise Exception("This will never be called.")


# ----------------------------------------------------------------------
def test_SingleArg():
    the_type = CreateFromMetadata(
        MyType,
        Mock(),
        Cardinality.CreateFromCode(),
        Metadata(
            Mock(),
            [
                MetadataItem(Mock(), SimpleElement[str](Mock(), "a"), IntegerExpression(Mock(), 2)),
            ],
        ),
    )

    assert isinstance(the_type, MyType)

    assert the_type.a == 2
    assert the_type.b == 10
    assert the_type.c is None


# ----------------------------------------------------------------------
def test_TwoArgs():
    the_type = CreateFromMetadata(
        MyType,
        Mock(),
        Cardinality.CreateFromCode(),
        Metadata(
            Mock(),
            [
                MetadataItem(Mock(), SimpleElement[str](Mock(), "b"), IntegerExpression(Mock(), 20)),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "a"), IntegerExpression(Mock(), 2)),
            ],
        ),
    )

    assert isinstance(the_type, MyType)

    assert the_type.a == 2
    assert the_type.b == 20
    assert the_type.c is None


# ----------------------------------------------------------------------
def test_ThreeArgs():
    the_type = CreateFromMetadata(
        MyType,
        Mock(),
        Cardinality.CreateFromCode(),
        Metadata(
            Mock(),
            [
                MetadataItem(Mock(), SimpleElement[str](Mock(), "a"), IntegerExpression(Mock(), 2)),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "b"), IntegerExpression(Mock(), 20)),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "c"), IntegerExpression(Mock(), 200)),
            ],
        ),
    )

    assert isinstance(the_type, MyType)

    assert the_type.a == 2
    assert the_type.b == 20
    assert the_type.c == 200


# ----------------------------------------------------------------------
def test_ErrorNoMetadata():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("MyType.__init__() missing 1 required positional argument: 'a' (filename <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        CreateFromMetadata(
            MyType,
            Range.Create(Path("filename"), 1, 2, 3, 4),
            Cardinality.CreateFromCode(),
            None,
        )


# ----------------------------------------------------------------------
def test_ComplexType():
    the_type = CreateFromMetadata(
        ComplexType,
        Mock(),
        Cardinality.CreateFromCode(),
        Metadata(
            Mock(),
            [
                MetadataItem(Mock(), SimpleElement[str](Mock(), "b"), BooleanExpression(Mock(), True)),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "f"), NumberExpression(Mock(), 3.14)),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "i"), IntegerExpression(Mock(), 123)),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "s"), StringExpression(Mock(), "hello!")),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "optional"), NoneExpression(Mock())),
                MetadataItem(Mock(), SimpleElement[str](Mock(), "variant"), BooleanExpression(Mock(), False)),

                MetadataItem(
                    Mock(),
                    SimpleElement[str](Mock(), "l"),
                    ListExpression(
                        Mock(),
                        [
                            BooleanExpression(Mock(), True),
                            BooleanExpression(Mock(), False),
                            BooleanExpression(Mock(), True),
                        ],
                    ),
                ),

                MetadataItem(
                    Mock(),
                    SimpleElement[str](Mock(), "t"),
                    TupleExpression(
                        Mock(),
                        (
                            IntegerExpression(Mock(), 10),
                            StringExpression(Mock(), "20"),
                        ),
                    ),
                ),

                MetadataItem(Mock(), SimpleElement[str](Mock(), "e"), StringExpression(Mock(), "Two")),
            ],
        ),
    )

    assert isinstance(the_type, ComplexType)

    assert the_type.b is True
    assert the_type.e == MyEnum.Two
    assert the_type.f == 3.14
    assert the_type.i == 123
    assert the_type.s == "hello!"

    assert the_type.optional is None
    assert the_type.variant is False

    assert the_type.l == [True, False, True]
    assert the_type.t == (10, "20", )


# ----------------------------------------------------------------------
def test_ErrorInvalidType():
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class BadType(FundamentalType):
        # ----------------------------------------------------------------------
        NAME: ClassVar[str]                                             = "Bad"
        SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]        = (object, )

        this_type_is_not_supported: ComplexType

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            raise Exception("This is never called")

    # ----------------------------------------------------------------------

    with pytest.raises(
        Exception,
        match=re.escape("'<class 'src.SimpleSchema.Schema.Elements.Types.FundamentalTypes.UnitTests.FundamentalTypeCreator_UnitTest.ComplexType'>' is not a supported python type."),
    ):
        CreateFromMetadata(
            BadType,
            Range.Create(Path("the_filename"), 10, 20, 30, 40),
            Cardinality.CreateFromCode(),
            Metadata(
                Mock(),
                [
                    MetadataItem(Mock(), SimpleElement[str](Mock(), "this_type_is_not_supported"), BooleanExpression(Mock(), True)),
                ],
            ),
        )
