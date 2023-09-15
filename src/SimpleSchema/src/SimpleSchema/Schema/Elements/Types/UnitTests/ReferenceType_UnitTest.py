# ----------------------------------------------------------------------
# |
# |  ReferenceType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-04-01 09:36:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ReferenceType.py"""

import re
import sys
import textwrap

from pathlib import Path
from unittest.mock import MagicMock as Mock
from typing import Optional, Union

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import DoesNotExist


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.ReferenceType import ReferenceType

    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement
    from SimpleSchema.Schema.Elements.Common.Visibility import Visibility

    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
    from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

    from SimpleSchema.Schema.Elements.Types.BasicType import BasicType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.IntegerType import IntegerType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.StringType import StringType
    from SimpleSchema.Schema.Elements.Types.ReferenceType  import ReferenceType
    from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
    from SimpleSchema.Schema.Elements.Types.VariantType import VariantType


# ----------------------------------------------------------------------
@pytest.mark.parametrize("is_source", [False, True])
@pytest.mark.parametrize("suppress_range_in_exceptions", [False, True])
@pytest.mark.parametrize(
    "cardinality",
    [
        Cardinality.CreateFromCode(),
        Cardinality.CreateFromCode(0, 1),
        Cardinality.CreateFromCode(0),
    ],
)
def test_Standard(
    cardinality: Cardinality,
    is_source: bool,
    suppress_range_in_exceptions: bool,
):
    range_mock = Mock()
    type_mock = Mock(spec=BasicType)
    visibility_mock = Mock()
    name_mock = Mock()
    metadata_mock = Mock()

    rt = ReferenceType(
        range_mock,
        visibility_mock,
        type_mock,
        name_mock,
        cardinality,
        metadata_mock,
        is_source=is_source,
        suppress_range_in_exceptions=suppress_range_in_exceptions,
    )

    assert rt.range is range_mock
    assert rt.type is type_mock
    assert rt.visibility is visibility_mock
    assert rt.name is name_mock
    assert rt.cardinality is cardinality
    assert rt.unresolved_metadata is metadata_mock
    assert rt.suppress_range_in_exceptions == suppress_range_in_exceptions

    if is_source:
        assert rt.category == ReferenceType.Category.Source
    elif cardinality.is_single:
        assert rt.category == ReferenceType.Category.Alias
    else:
        assert rt.category == ReferenceType.Category.Reference


# ----------------------------------------------------------------------
class TestCreate(object):
    # ----------------------------------------------------------------------
    @pytest.mark.parametrize(
        "cardinality",
        [
            Cardinality.CreateFromCode(),
            Cardinality.CreateFromCode(0),
        ],
    )
    def test_Basic(
        self,
        cardinality: Cardinality,
    ):
        range_mock = Mock()
        visibility_mock = Mock()
        name_mock = Mock()

        type_mock = Mock(spec=BasicType)
        type_mock.range = range_mock

        metadata_mock = Mock()

        rt = ReferenceType.Create(
            visibility_mock,
            name_mock,
            type_mock,
            cardinality,
            metadata_mock,
        )

        assert rt.range is range_mock
        assert rt.visibility is visibility_mock
        assert rt.name is name_mock
        assert rt.cardinality is cardinality
        assert rt.unresolved_metadata is metadata_mock

        assert rt.category == ReferenceType.Category.Source

        if cardinality.is_single:
            assert rt.type is type_mock
        else:
            assert isinstance(rt.type, ReferenceType)
            assert rt.type.category == ReferenceType.Category.Source
            assert rt.type.type is type_mock

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize(
        "cardinality",
        [
            Cardinality.CreateFromCode(),
            Cardinality.CreateFromCode(0),
        ],
    )
    def test_Reference(
        self,
        cardinality: Cardinality,
    ):
        range_mock = Mock()
        visibility_mock = Mock()
        name_mock = Mock()

        type_mock = Mock(spec=ReferenceType)
        type_mock.range = range_mock
        type_mock.cardinality = Mock()
        type_mock.category = ReferenceType.Category.Reference

        metadata_mock = Mock()

        rt = ReferenceType.Create(
            visibility_mock,
            name_mock,
            type_mock,
            cardinality,
            metadata_mock,
        )

        assert rt.range is range_mock
        assert rt.visibility is visibility_mock
        assert rt.name is name_mock
        assert rt.unresolved_metadata is metadata_mock

        assert isinstance(rt.type, ReferenceType)
        assert rt.type.category == ReferenceType.Category.Reference
        assert rt.type is type_mock

        if cardinality.is_single:
            assert rt.cardinality is type_mock.cardinality
            assert rt.category == ReferenceType.Category.Alias
        else:
            assert rt.cardinality is cardinality

    # ----------------------------------------------------------------------
    def test_MetadataSimplification(self):
        rt = ReferenceType.Create(
            Mock(),  # visibility
            Mock(),  # name
            Mock(),  # the_type
            Mock(),  # cardinality
            Metadata(Mock(), []),
        )

        assert rt.unresolved_metadata is None


# ----------------------------------------------------------------------
def test_ErrorOptionalToOptional():
    referenced_type = Mock(spec=BasicType)
    referenced_type.range = Mock()

    optional_type = _Create(referenced_type, Cardinality.CreateFromCode(0, 1), range_value=Range.Create(Path("filename"), 1, 2, 3, 4))

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            textwrap.dedent(
                """\
                Optional reference types may not reference optional reference types.

                    - filename <Ln 10, Col 20 -> Ln 30, Col 40>
                    - filename <Ln 1, Col 2 -> Ln 3, Col 4>
                """,
            ),
        )
    ):
        _Create(
            optional_type,
            Cardinality.CreateFromCode(
                0,
                1,
                range_value=Range.Create(Path("filename"), 10, 20, 30, 40),
            ),
        )


# ----------------------------------------------------------------------
def test_ResolveMetadata():
    rt = _Create(Mock(spec=BasicType), Cardinality.CreateFromCode(), metadata=None)

    assert rt.is_metadata_resolved is False
    assert rt.unresolved_metadata is None

    with pytest.raises(
        RuntimeError,
        match=re.escape("Metadata has not yet been resolved."),
    ):
        rt.resolved_metadata

    rt.ResolveMetadata({})

    assert rt.is_metadata_resolved is True
    assert rt.resolved_metadata == {}

    with pytest.raises(
        RuntimeError,
        match=re.escape("Metadata has been resolved."),
    ):
        rt.unresolved_metadata

    with pytest.raises(
        RuntimeError,
        match=re.escape("Metadata has already been resolved."),
    ):
        rt.ResolveMetadata({})


# ----------------------------------------------------------------------
def test_IsShared():
    rt = _Create(Mock(spec=BasicType), Cardinality.CreateFromCode())

    assert rt.is_shared_resolved is False

    with pytest.raises(
        RuntimeError,
        match=re.escape("Shared status has not been resolved."),
    ):
        rt.is_shared

    rt.ResolveIsShared(True)

    assert rt.is_shared_resolved is True
    assert rt.is_shared is True

    with pytest.raises(
        RuntimeError,
        match=re.escape("Shared status has already been resolved."),
    ):
        rt.ResolveIsShared(True)


# ----------------------------------------------------------------------
class TestResolve(object):
    # ----------------------------------------------------------------------
    @pytest.mark.parametrize(
        "cardinality",
        [
            Cardinality.CreateFromCode(),
            Cardinality.CreateFromCode(0),
            Cardinality.CreateFromCode(0, 1),
        ],
    )
    def test_Basic(
        self,
        cardinality: Cardinality,
    ):
        basic_type = Mock(spec=BasicType)
        basic_type.range = Mock()

        rt = _Create(basic_type, cardinality)

        with rt.Resolve() as resolved_type:
            assert resolved_type is rt

    # ----------------------------------------------------------------------
    def test_SingleReference(self):
        referenced_type = _Create(Mock(spec=BasicType), Cardinality.CreateFromCode())

        rt = _Create(referenced_type, Cardinality.CreateFromCode())

        with rt.Resolve() as resolved_type:
            assert resolved_type is referenced_type

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize(
        "cardinality",
        [
            Cardinality.CreateFromCode(0),
            Cardinality.CreateFromCode(0, 1),
        ],
    )
    def test_MultipleReference(
        self,
        cardinality: Cardinality,
    ):
        referenced_type = _Create(Mock(spec=BasicType), Cardinality.CreateFromCode())

        rt = _Create(referenced_type, cardinality)

        with rt.Resolve() as resolved_type:
            assert resolved_type is rt

    # ----------------------------------------------------------------------
    def test_ErrorSingle(self):
        rt = _Create(
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(),
            range_value=Range.Create(Path("the--filename"), 2, 4, 6, 8),
        )

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("An error (the--filename <Ln 2, Col 4 -> Ln 6, Col 8>)"),
        ):
            with rt.Resolve():
                raise Exception("An error")

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    An error

                        - This unique file <Ln 1, Col 2 -> Ln 3, Col 4>
                        - the--filename <Ln 2, Col 4 -> Ln 6, Col 8>
                    """,
                ),
            ),
        ):
            with rt.Resolve():
                raise SimpleSchemaException(Range.Create(Path("This unique file"), 1, 2, 3, 4), "An error")

    # ----------------------------------------------------------------------
    def test_ErrorReference(self):
        rt = _Create(
            _Create(
                Mock(spec=BasicType),
                Cardinality.CreateFromCode(),
                range_value=Range.Create(Path("filename1"), 2, 4, 6, 8),
            ),
            Cardinality.CreateFromCode(),
            range_value=Range.Create(Path("filename2"), 6, 8, 10, 12),
        )

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    An error

                        - filename1 <Ln 2, Col 4 -> Ln 6, Col 8>
                        - filename2 <Ln 6, Col 8 -> Ln 10, Col 12>
                    """,
                ),
            ),
        ):
            with rt.Resolve():
                raise Exception("An error")

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    An error

                        - filename3 <Ln 14, Col 16 -> Ln 18, Col 20>
                        - filename1 <Ln 2, Col 4 -> Ln 6, Col 8>
                        - filename2 <Ln 6, Col 8 -> Ln 10, Col 12>
                    """,
                ),
            ),
        ):
            with rt.Resolve():
                raise SimpleSchemaException(Range.Create(Path("filename3"), 14, 16, 18, 20), "An error")


# ----------------------------------------------------------------------
class TestToPython(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        rt = _Create(
            StringType(Mock()),
            Cardinality.CreateFromCode(),
        )

        assert rt.ToPython("foo") == "foo"
        assert rt.ToPython(StringExpression(Mock(), "bar")) == "bar"

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        rt = _Create(
            StringType(Mock()),
            Cardinality.CreateFromCode(2, 2),
        )

        assert rt.ToPython(["foo", "bar"]) == ["foo", "bar"]

        assert rt.ToPython(
            [
                StringExpression(Mock(), "baz"),
                StringExpression(Mock(), "biz"),
            ],
        ) == ["baz", "biz"]

    # ----------------------------------------------------------------------
    def test_Optional(self):
        rt = _Create(
            StringType(Mock()),
            Cardinality.CreateFromCode(0, 1),
        )

        assert rt.ToPython("foo") == "foo"
        assert rt.ToPython(None) is None
        assert rt.ToPython(StringExpression(Mock(), "bar")) == "bar"
        assert rt.ToPython(NoneExpression(Mock())) is None

    # ----------------------------------------------------------------------
    def test_ReferenceReference(self):
        rt = _Create(
            _Create(
                StringType(Mock()),
                Cardinality.CreateFromCode(),
            ),
            Cardinality.CreateFromCode(),
        )

        assert rt.ToPython("foo") == "foo"

    # ----------------------------------------------------------------------
    def test_SingleVariant(self):
        rt = _Create(
            VariantType(
                Mock(),
                [
                    _Create(StringType(Mock()), Cardinality.CreateFromCode()),
                    _Create(IntegerType(Mock()), Cardinality.CreateFromCode()),
                ],
            ),
            Cardinality.CreateFromCode(),
        )

        rt.ToPython("foo") == "foo"
        rt.ToPython(123) == 123
        rt.ToPython(StringExpression(Mock(), "bar")) == "bar"
        rt.ToPython(IntegerExpression(Mock(), 456)) == 456

    # ----------------------------------------------------------------------
    def test_SingleVariantWithMultipleChildren(self):
        rt = _Create(
            VariantType(
                Mock(),
                [
                    _Create(StringType(Mock()), Cardinality.CreateFromCode(2, 2)),
                    _Create(IntegerType(Mock()), Cardinality.CreateFromCode(3, 3)),
                ],
            ),
            Cardinality.CreateFromCode(),
        )

        assert rt.ToPython(["foo", "bar"]) == ["foo", "bar"]
        assert rt.ToPython([1, 2, 3]) == [1, 2, 3]

        assert rt.ToPython(
            ListExpression(
                Mock(),
                [
                    StringExpression(Mock(), "baz"),
                    StringExpression(Mock(), "biz"),
                ],
            ),
        ) == ["baz", "biz"]

    # ----------------------------------------------------------------------
    def test_MultipleVariant(self):
        rt = _Create(
            VariantType(
                Mock(),
                [
                    _Create(StringType(Mock()), Cardinality.CreateFromCode(2, 2)),
                    _Create(IntegerType(Mock()), Cardinality.CreateFromCode(2, 2)),
                ],
            ),
            Cardinality.CreateFromCode(3, 3),
        )

        assert rt.ToPython(
            [
                ["foo", "bar"],
                [1, 2],
                [3, 4],
            ],
        ) == [
            ["foo", "bar"],
            [1, 2],
            [3, 4],
        ]

        assert rt.ToPython(
            ListExpression(
                Mock(),
                [
                    ListExpression(Mock(), [StringExpression(Mock(), "foo"), StringExpression(Mock(), "bar")]),
                    ListExpression(Mock(), [IntegerExpression(Mock(), 1), IntegerExpression(Mock(), 2)]),
                    ListExpression(Mock(), [IntegerExpression(Mock(), 3), IntegerExpression(Mock(), 4)]),
                ],
            ),
        ) == [
            ["foo", "bar"],
            [1, 2],
            [3, 4],
        ]


# ----------------------------------------------------------------------
class TestDisplayType(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        rt = _Create(
            IntegerType(Mock()),
            Cardinality.CreateFromCode(),
        )

        assert rt.display_type == "Integer"

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        rt = _Create(
            IntegerType(Mock()),
            Cardinality.CreateFromCode(2, 2),
        )

        assert rt.display_type == "Integer[2]"

    # ----------------------------------------------------------------------
    def test_SingleWithConstraints(self):
        rt = _Create(
            IntegerType(Mock(), min=5),
            Cardinality.CreateFromCode(),
        )

        assert rt.display_type == "Integer {>= 5}"

    # ----------------------------------------------------------------------
    def test_MultipleWithConstraints(self):
        rt = _Create(
            IntegerType(Mock(), min=5),
            Cardinality.CreateFromCode(2, 2),
        )

        assert rt.display_type == "<Integer {>= 5}>[2]"


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Create(
    the_type: Union[BasicType, ReferenceType],
    cardinality: Cardinality,
    *,
    range_value: Optional[Range]=None,
    visibility: Optional[Visibility]=None,
    metadata: Union[DoesNotExist, None, Metadata]=DoesNotExist.instance,
    suppress_range_in_exceptions: bool=False,
) -> ReferenceType:
    if visibility is not None:
        visibility_value = Mock()
        visibility_value.value = visibility
    else:
        visibility_value = Mock()

    return ReferenceType.Create(
        visibility_value,
        Mock(), # name
        the_type,
        cardinality,
        Mock() if metadata is DoesNotExist.instance else metadata,
        range_value=range_value or Mock(),
        suppress_range_in_exceptions=suppress_range_in_exceptions,
    )
