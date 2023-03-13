# ----------------------------------------------------------------------
# |
# |  ReferenceType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-17 13:35:06
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
def test_Standard():
    range_mock = Mock()
    type_mock = Mock(spec=BasicType)
    visibility_mock = Mock()
    name_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    rt = ReferenceType(
        range_mock,
        type_mock,
        visibility_mock,
        name_mock,
        cardinality_mock,
        metadata_mock,
        force_single_cardinality=False,
        was_dynamically_generated=False,
    )

    assert rt.range is range_mock
    assert rt.type is type_mock
    assert rt.visibility is visibility_mock
    assert rt.name is name_mock
    assert rt.cardinality is cardinality_mock
    assert rt.unresolved_metadata is metadata_mock
    assert rt.flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.BasicRef | ReferenceType.Flag.Alias


# ----------------------------------------------------------------------
class TestCreate(object):
    # ----------------------------------------------------------------------
    def test_SingleBasic(self):
        range_mock = Mock()
        visibility_mock = Mock()
        name_mock = Mock()
        type_mock = Mock(spec=BasicType)
        metadata_mock = Mock()

        rt = ReferenceType.Create(
            range_mock,
            visibility_mock,
            name_mock,
            type_mock,
            Cardinality.CreateFromCode(),
            metadata_mock,
        )

        assert rt.range is range_mock
        assert rt.type is type_mock
        assert rt.visibility is visibility_mock
        assert rt.name is name_mock
        assert rt.cardinality.is_single
        assert rt.unresolved_metadata is metadata_mock
        assert rt.flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.BasicRef | ReferenceType.Flag.Alias

    # ----------------------------------------------------------------------
    def test_MultipleBasic(self):
        range_mock = Mock()
        visibility_mock = Mock()

        name_mock = Mock()
        name_mock.value = "The type name"

        type_mock = Mock(spec=BasicType)
        type_mock.range = Mock()

        metadata_mock = Mock()

        cardinality = Cardinality.CreateFromCode(1, None)

        rt = ReferenceType.Create(
            range_mock,
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
        assert rt.flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.BasicCollectionRef | ReferenceType.Flag.ReferenceRef | ReferenceType.Flag.Type

        assert isinstance(rt.type, ReferenceType), rt.type

        assert rt.type.range is range_mock
        assert rt.type.type is type_mock
        assert rt.type.visibility == SimpleElement[Visibility](type_mock.range, Visibility.Private)
        assert rt.type.name.value != name_mock.value
        assert rt.type.cardinality.is_single
        assert rt.type.unresolved_metadata is None
        assert rt.type.flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.DynamicallyGenerated | ReferenceType.Flag.BasicRef | ReferenceType.Flag.Type

    # ----------------------------------------------------------------------
    def test_SingleReference(self):
        range_mock = Mock()
        visibility_mock = Mock()
        name_mock = Mock()
        metadata_mock = Mock()

        type_mock = Mock(spec=ReferenceType)
        type_mock.flags = 0
        type_mock.cardinality = Mock()

        rt = ReferenceType.Create(
            range_mock,
            visibility_mock,
            name_mock,
            type_mock,
            Cardinality.CreateFromCode(),
            metadata_mock,
        )

        assert rt.range is range_mock
        assert rt.visibility is visibility_mock
        assert rt.name is name_mock
        assert rt.type is type_mock
        assert rt.cardinality.is_single
        assert rt.unresolved_metadata is metadata_mock
        assert rt.flags == ReferenceType.Flag.ReferenceRef | ReferenceType.Flag.Alias

    # ----------------------------------------------------------------------
    def test_ContainerReference(self):
        range_mock = Mock()
        visibility_mock = Mock()
        name_mock = Mock()

        type_mock = Mock(spec=ReferenceType)
        type_mock.flags = 0
        type_mock.range = Mock()

        metadata_mock = Mock()

        rt = ReferenceType.Create(
            range_mock,
            visibility_mock,
            name_mock,
            type_mock,
            Cardinality.CreateFromCode(0, 10),
            metadata_mock,
        )

        assert rt.range is range_mock
        assert rt.visibility is visibility_mock
        assert rt.name is name_mock
        assert rt.type is type_mock
        assert rt.cardinality.is_container
        assert rt.unresolved_metadata is metadata_mock
        assert rt.flags == ReferenceType.Flag.ReferenceRef | ReferenceType.Flag.Type

    # ----------------------------------------------------------------------
    def test_MetadataReplacement(self):
        rt = ReferenceType.Create(
            Mock(),
            Mock(),
            Mock(),
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(),
            Metadata(Mock(), []),
        )

        assert rt.unresolved_metadata is None


# ----------------------------------------------------------------------
class TestFlags(object):
    # ----------------------------------------------------------------------
    def test_SingleBasic(self):
        assert _Create(
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(),
        ).flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.BasicRef | ReferenceType.Flag.Alias

    # ----------------------------------------------------------------------
    def test_MultipleBasic(self):
        assert _Create(
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(0, None),
        ).flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.BasicRef | ReferenceType.Flag.Type

    # ----------------------------------------------------------------------
    def test_ReferenceStructure(self):
        assert _Create(
            Mock(spec=StructureType),
            Cardinality.CreateFromCode(),
        ).flags == ReferenceType.Flag.DefinedInline | ReferenceType.Flag.StructureRef | ReferenceType.Flag.BasicRef | ReferenceType.Flag.Alias

    # ----------------------------------------------------------------------
    def test_Reference(self):
        reference_mock = Mock(spec=ReferenceType)
        reference_mock.flags = 0
        reference_mock.cardinality = Mock()

        assert _Create(
            reference_mock,
            Cardinality.CreateFromCode(),
        ).flags == ReferenceType.Flag.ReferenceRef | ReferenceType.Flag.Alias

    # ----------------------------------------------------------------------
    def test_DynamicallyGeneratedReference (self):
        reference_mock = Mock(spec=ReferenceType)
        reference_mock.flags = ReferenceType.Flag.DynamicallyGenerated
        reference_mock.cardinality = Mock()

        assert _Create(
            reference_mock,
            Cardinality.CreateFromCode(),
        ).flags == ReferenceType.Flag.BasicCollectionRef | ReferenceType.Flag.ReferenceRef | ReferenceType.Flag.Alias

    # ----------------------------------------------------------------------
    def test_DynamicallyGeneratedReferenceToStructure(self):
        reference_mock = Mock(spec=ReferenceType)
        reference_mock.flags = ReferenceType.Flag.DynamicallyGenerated | ReferenceType.Flag.StructureRef
        reference_mock.cardinality = Mock()

        assert _Create(
            reference_mock,
            Cardinality.CreateFromCode(),
        ).flags == ReferenceType.Flag.StructureCollectionRef | ReferenceType.Flag.BasicCollectionRef | ReferenceType.Flag.ReferenceRef | ReferenceType.Flag.Alias


# ----------------------------------------------------------------------
class TestResolve(object):
    # ----------------------------------------------------------------------
    def test_SingleBasic(self):
        rt = _Create(
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(),
        )

        with rt.Resolve() as resolved_type:
            assert resolved_type is rt

    # ----------------------------------------------------------------------
    def test_MultipleBasic(self):
        rt = _Create(
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(10, 10),
        )

        with rt.Resolve() as resolved_type:
            assert resolved_type is rt

    # ----------------------------------------------------------------------
    def test_ReferenceStructure(self):
        rt = _Create(
            Mock(spec=StructureType),
            Cardinality.CreateFromCode(),
        )

        with rt.Resolve() as resolved_type:
            assert resolved_type is rt

    # ----------------------------------------------------------------------
    def test_SingleReference(self):
        referenced_type = _Create(
            Mock(spec=BasicType),
            Cardinality.CreateFromCode(),
        )

        rt = _Create(
            referenced_type,
            Cardinality.CreateFromCode(),
        )

        with rt.Resolve() as resolved_type:
            assert resolved_type is referenced_type

    # ----------------------------------------------------------------------
    def test_MultipleReference(self):
        referenced_mock = Mock(spec=ReferenceType)
        referenced_mock.range = Mock()
        referenced_mock.flags = 0

        rt = _Create(
            referenced_mock,
            Cardinality.CreateFromCode(10, 10),
        )

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
    def test_ErrorReferenceReferenceStructure(self):
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
def test_ErrorOptionalToOptional():
    referenced_type = _Create(Mock(spec=BasicType), Cardinality.CreateFromCode(0, 1), range_value=Range.Create(Path("filename"), 1, 2, 3, 4))

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
        _Create(referenced_type, Cardinality.CreateFromCode(0, 1), range_value=Range.Create(Path("filename"), 10, 20, 30, 40))


# ----------------------------------------------------------------------
def test_Resolve():
    rt = _Create(Mock(spec=BasicType), Cardinality.CreateFromCode(), metadata=None)

    assert rt.is_metadata_resolved is False
    assert rt.unresolved_metadata is None

    with pytest.raises(AssertionError):
        rt.resolved_metadata

    rt.ResolveMetadata({})

    assert rt.is_metadata_resolved is True
    assert rt.resolved_metadata == {}

    with pytest.raises(AssertionError):
        rt.unresolved_metadata

    with pytest.raises(AssertionError):
        rt.ResolveMetadata({})


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Create(
    the_type: Union[BasicType, ReferenceType],
    cardinality: Cardinality,
    *,
    force_single_cardinality: bool=False,
    was_dynamically_generated: bool=False,
    range_value: Optional[Range]=None,
    metadata: Union[DoesNotExist, None, Metadata]=DoesNotExist.instance,
) -> ReferenceType:
    return ReferenceType(
        range_value or Mock(),
        the_type,
        Mock(),
        Mock(),
        cardinality,
        Mock() if metadata is DoesNotExist.instance else metadata,
        force_single_cardinality=force_single_cardinality,
        was_dynamically_generated=was_dynamically_generated,
    )
