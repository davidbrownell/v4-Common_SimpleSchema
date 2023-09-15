# ----------------------------------------------------------------------
# |
# |  Normalize_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-09 13:41:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""\
Unit tests for Normalize.py

Note that these tests are actually Integration tests (as they are using more than one
class or function), but are named "UnitTests" to ensure that they participate in code
coverage collection and enforcement.
"""

import inspect
import re
import sys
import textwrap

from pathlib import Path
from typing import cast, Optional, Tuple, Union
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement
    from SimpleSchema.Schema.Elements.Common.Visibility import Visibility

    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement

    from SimpleSchema.Schema.Elements.Types.BasicType import BasicType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.BooleanType import BooleanType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.IntegerType import IntegerType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.NumberType import NumberType
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.StringType import StringType
    from SimpleSchema.Schema.Elements.Types.ReferenceType import ReferenceType
    from SimpleSchema.Schema.Elements.Types.TupleType import TupleType

    from SimpleSchema.Schema.MetadataAttributes.ElementAttributes import NameMetadataAttribute
    from SimpleSchema.Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute

    from SimpleSchema.Schema.Parse import TestHelpers
    from SimpleSchema.Schema.Parse.ANTLR.Parse import Parse
    from SimpleSchema.Schema.Parse.Normalize.Normalize import Normalize, Flag as NormalizeFlag
    from SimpleSchema.Schema.Parse.TypeResolver.Resolve import Resolve


# code_coverage: include = ../Normalize.py


# ----------------------------------------------------------------------
def test_Standard():
    _Test(
        textwrap.dedent(
            """\
            Structure ->
                statement: String
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_Reference():
    _Test(
        textwrap.dedent(
            """\
            Structure ->
                statement: String

            structures: Structure+
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_IndirectReference():
    _Test(
        textwrap.dedent(
            """\
            Type: String
            Types: Type+
            TypesCollection: Types*

            type: Type
            types: Types
            types_collection: TypesCollection
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_StructureCollection():
    _Test(
        textwrap.dedent(
            """\
            Structure ->
                statement: String
            +

            structures: Structure
            """,
        ),
    )


# ----------------------------------------------------------------------
class TestExtensionMethods(object):
    content                                 = textwrap.dedent(
        """\
        Foo()
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(
            self.__class__.content,
            None,
            set(["Foo", ]),
        )

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The extension 'Foo' is not recognized. ({} <Ln 1, Col 1 -> Ln 1, Col 4>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=NormalizeFlag.DisableUnsupportedExtensions,
        )


# ----------------------------------------------------------------------
class TestRootItemStatements(object):
    content                                 = textwrap.dedent(
        """\
        item: String
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Root items are not supported. ({} <Ln 1, Col 1 -> Ln 2, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                self.__class__.content,
                flags=_default_flags & ~NormalizeFlag.AllowRootItems,
            )

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=(_default_flags & ~NormalizeFlag.AllowRootItems) | NormalizeFlag.DisableUnsupportedRootElements,
        )


# ----------------------------------------------------------------------
class TestNestedItemStatements(object):
    content                                 = textwrap.dedent(
        """\
        Structure ->
            item: String
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Nested items are not supported. ({} <Ln 2, Col 5 -> Ln 3, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                self.__class__.content,
                flags=_default_flags & ~NormalizeFlag.AllowNestedItems,
            )

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=(_default_flags & ~NormalizeFlag.AllowNestedItems) | NormalizeFlag.DisableUnsupportedNestedElements,
        )


# ----------------------------------------------------------------------
class TestRootStructures(object):
    content                                 = textwrap.dedent(
        """\
        Structure ->
            item: String
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Root structures are not supported. ({} <Ln 1, Col 1 -> Ln 3, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                self.__class__.content,
                flags=_default_flags & ~NormalizeFlag.AllowRootStructures,
            )

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=(_default_flags & ~NormalizeFlag.AllowRootStructures) | NormalizeFlag.DisableUnsupportedRootElements,
        )


# ----------------------------------------------------------------------
class TestNestedStructures(object):
    content                                 = textwrap.dedent(
        """\
        Structure ->
            Nested ->
                item: String
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Nested structures are not supported. ({} <Ln 2, Col 5 -> Ln 4, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                self.__class__.content,
                flags=_default_flags & ~NormalizeFlag.AllowNestedStructures,
            )

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=(_default_flags & ~NormalizeFlag.AllowNestedStructures) | NormalizeFlag.DisableUnsupportedNestedElements,
        )


# ----------------------------------------------------------------------
class TestRootTypes(object):
    content                                 = textwrap.dedent(
        """\
        Type: String
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Root types are not supported. ({} <Ln 1, Col 1 -> Ln 2, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                self.__class__.content,
                flags=_default_flags & ~NormalizeFlag.AllowRootTypes,
            )

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=(_default_flags & ~NormalizeFlag.AllowRootTypes) | NormalizeFlag.DisableUnsupportedRootElements,
        )


# ----------------------------------------------------------------------
class TestNestedTypes(object):
    content                                 = textwrap.dedent(
        """\
        Structure ->
            Type: String
        """,
    )

    # ----------------------------------------------------------------------
    def test_Supported(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Nested types are not supported. ({} <Ln 2, Col 5 -> Ln 3, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                self.__class__.content,
                flags=_default_flags & ~NormalizeFlag.AllowNestedTypes,
            )

    # ----------------------------------------------------------------------
    def test_Disabled(self):
        _Test(
            self.__class__.content,
            flags=(_default_flags & ~NormalizeFlag.AllowNestedTypes) | NormalizeFlag.DisableUnsupportedNestedElements,
        )


# ----------------------------------------------------------------------
class TestFlatten(object):
    # ----------------------------------------------------------------------
    class TestBasic(object):
        content                             = textwrap.dedent(
            """\
            NoItems: String ->
                pass

            WithItems: Integer { min: 12 } ->
                item: String
            """,
        )

        # ----------------------------------------------------------------------
        def test_NoFlatten(self):
            _Test(self.__class__.content)

        # ----------------------------------------------------------------------
        def test_Flatten(self):
            _Test(
                self.__class__.content,
                flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
            )

    # ----------------------------------------------------------------------
    class TestStructureBase(object):
        content                             = textwrap.dedent(
            """\
            Base ->
                base1: String
                base2: Integer

            NoItems: Base ->
                pass

            WithItems: Base ->
                item: Number
            """,
        )

        # ----------------------------------------------------------------------
        def test_NoFlatten(self):
            _Test(self.__class__.content)

        # ----------------------------------------------------------------------
        def test_Flatten(self):
            _Test(
                self.__class__.content,
                flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
            )

    # ----------------------------------------------------------------------
    class TestStructuresBases(object):
        content                             = textwrap.dedent(
            """\
            Base1 ->
                base1_a: String
                base1_b: Integer

            Base2 ->
                base2_a: DateTime

            Base3: Base2 ->
                base3_a: Guid

            NoItems: Base1, Base2 ->
                pass

            WithItems: Base3, Base1 ->
                item: Number
            """,
        )

        # ----------------------------------------------------------------------
        def test_NoFlatten(self):
            _Test(self.__class__.content)

        # ----------------------------------------------------------------------
        def test_Flatten(self):
            _Test(
                self.__class__.content,
                flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
            )

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateItem1(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The name 'item' (defined at {entry_point} <Ln 2, Col 5 -> Ln 2, Col 9>) has already been defined at {entry_point} <Ln 5, Col 5 -> Ln 6, Col 1>. ({entry_point} <Ln 4, Col 1 -> Ln 6, Col 1>)".format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Base1 ->
                        item: String

                    Conflict: Base1 ->
                        item: Number
                    """,
                ),
                flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
            )

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateItem2(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The name 'item' (defined at {entry_point} <Ln 5, Col 5 -> Ln 5, Col 9>) has already been defined at {entry_point} <Ln 2, Col 5 -> Ln 3, Col 1>. ({entry_point} <Ln 7, Col 1 -> Ln 9, Col 1>)".format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Base1 ->
                        item: String

                    Base2 ->
                        item: Number

                    Conflict: Base1, Base2 ->
                        pass
                    """,
                ),
                flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
            )

    # ----------------------------------------------------------------------
    def test_ResolutionOrder(self):
        _Test(
            textwrap.dedent(
                """\
                # Note that these structures are defined "backwards".

                Derived: Base1 ->
                    pass

                Base1: Base2 ->
                    base1: String

                Base2 ->
                    base2: String
                """,
            ),
            flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
        )

    # ----------------------------------------------------------------------
    def test_TypesAreNotFlattened(self):
        _Test(
            textwrap.dedent(
                """\
                Base ->
                    Type: String
                    item: Type

                Derived: Base ->
                    pass
                """,
            ),
            flags=_default_flags | NormalizeFlag.FlattenStructureHierarchies,
        )


# ----------------------------------------------------------------------
class TestDisableEmptyStructures(object):
    content                                 = textwrap.dedent(
        """\
        EmptyStructure ->
            pass
        """,
    )

    # ----------------------------------------------------------------------
    def test_Standard(self):
        _Test(self.__class__.content)

    # ----------------------------------------------------------------------
    def test_DisableEmptyStructures(self):
        _Test(
            self.__class__.content,
            flags=_default_flags | NormalizeFlag.DisableEmptyStructures,
        )


# ----------------------------------------------------------------------
_default_attribute_flags: MetadataAttribute.Flag        = MetadataAttribute.Flag.NoRestrictions


# ----------------------------------------------------------------------
def _CreateAttribute(
    type: BasicType,
    flags: Optional[MetadataAttribute.Flag]=None,
    name: Optional[str]=None,
    cardinality: Optional[Cardinality]=None,
) -> MetadataAttribute:
    if flags is None:
        flags = _default_attribute_flags
    if name is None:
        name = type.NAME.lower()

    attribute = MetadataAttribute(flags, name, type)

    if cardinality is not None:
        object.__setattr__(attribute, "cardinality", cardinality)

    return attribute


# ----------------------------------------------------------------------
class TestMetadata(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def test_Types(self):
        # ----------------------------------------------------------------------
        def _CreateReferenceType(
            basic_type: BasicType,
        ) -> ReferenceType:
            return ReferenceType.Create(
                SimpleElement[Visibility](Range.CreateFromCode(), Visibility.Private),
                SimpleElement[str](Range.CreateFromCode(), "Type"),
                basic_type,
                Cardinality.CreateFromCode(1, 1),
                None,
            )

        # ----------------------------------------------------------------------

        _Test(
            textwrap.dedent(
                """\
                Structure ->
                    pass
                {
                    boolean: True
                    integer: 1235
                    list: ["One", "Two", "Three", ]
                    number: 3.14
                    optional: None
                    string: "Hello, world!"
                    tuple: (1, "two", 3.0)
                }
                """,
            ),
            [
                _CreateAttribute(BooleanType(Range.CreateFromCode())),
                _CreateAttribute(IntegerType(Range.CreateFromCode())),
                _CreateAttribute(
                    StringType(Range.CreateFromCode()),
                    name="list",
                    cardinality=Cardinality.CreateFromCode(1, None),
                ),
                _CreateAttribute(NumberType(Range.CreateFromCode())),
                _CreateAttribute(
                    StringType(Range.CreateFromCode()),
                    name="optional",
                    cardinality=Cardinality.CreateFromCode(0, 1),
                ),
                _CreateAttribute(StringType(Range.CreateFromCode())),
                _CreateAttribute(
                    TupleType(
                        Range.CreateFromCode(),
                        [
                            _CreateReferenceType(IntegerType(Range.CreateFromCode())),
                            _CreateReferenceType(StringType(Range.CreateFromCode())),
                            _CreateReferenceType(NumberType(Range.CreateFromCode())),
                        ],
                    ),
                ),
            ],
        )

    # ----------------------------------------------------------------------
    def test_Locations(self):
        _Test(
            textwrap.dedent(
                """\
                # Metadata can appear in many different locations; ensure that they
                # are all resolved.

                Structure: String { integer: 1 } ->
                    item: Number { integer: 2 }

                    Type: String { integer: 3 }
                { integer: 4 }
                """,
            ),
            [
                _CreateAttribute(IntegerType(Range.CreateFromCode())),
            ],
        )

    # ----------------------------------------------------------------------
    class TestInvalidMetadataItem(object):
        content                             = textwrap.dedent(
            """\
            Structure ->
                pass
            {
                not_supported: True
            }
            """,
        )

        # ----------------------------------------------------------------------
        def test_Standard(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'not_supported' is not supported. ({} <Ln 4, Col 5 -> Ln 4, Col 18>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(self.__class__.content)

        # ----------------------------------------------------------------------
        def test_Disable(self):
            _Test(
                self.__class__.content,
                flags=_default_flags | NormalizeFlag.DisableUnsupportedMetadata,
            )

    # ----------------------------------------------------------------------
    class TestElement(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="root",
                flags=MetadataAttribute.Flag.Root,
            ),
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="nested",
                flags=MetadataAttribute.Flag.Nested,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    item: String { root: 1 }

                    Structure: String { root: 2 } ->
                        item: String { nested: 100 }

                        Nested: String { nested: 101 } ->
                            pass
                        { nested: 102 }

                    { root: 3 }

                    Type: String { root: 4 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRootItem(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The element is not a nested element. ({} <Ln 1, Col 16 -> Ln 1, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { nested: 100 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRootStructure(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The element is not a nested element. ({} <Ln 3, Col 3 -> Ln 3, Col 14>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            pass
                        { nested: 100 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRootType(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The element is not a nested element. ({} <Ln 1, Col 16 -> Ln 1, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Type: String { nested: 100 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRootBase(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The element is not a nested element. ({} <Ln 1, Col 21 -> Ln 1, Col 32>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure: String { nested: 100 } ->
                            pass
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNestedItem(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a root element. ({} <Ln 2, Col 20 -> Ln 2, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            item: String { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNestedStructure(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a root element. ({} <Ln 4, Col 7 -> Ln 4, Col 14>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            Nested ->
                                pass
                            { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNestedType(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a root element. ({} <Ln 2, Col 20 -> Ln 2, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            Type: String { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNestedBase(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a root element. ({} <Ln 2, Col 22 -> Ln 2, Col 29>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            Nested: String { root: 1 } ->
                                pass
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestItem(object):
        root_attribute                      = _CreateAttribute(
            StringType(Range.CreateFromCode()),
            name="root",
            flags=MetadataAttribute.Flag.Item | MetadataAttribute.Flag.Root,
        )

        nested_attribute                    = _CreateAttribute(
            IntegerType(Range.CreateFromCode()),
            name="nested",
            flags=MetadataAttribute.Flag.Item | MetadataAttribute.Flag.Nested,
        )

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    root: Date { root: "value" }

                    Structure ->
                        nested: Date { nested: 0 }
                    """,
                ),
                [
                    self.__class__.root_attribute,
                    self.__class__.nested_attribute,
                ],
            )

        # ----------------------------------------------------------------------
        def test_ErrorWrongType(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not an item statement. ({} <Ln 3, Col 3 -> Ln 3, Col 16>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            pass
                        { root: "value" }
                        """,
                    ),
                    [
                        self.__class__.root_attribute,
                    ],
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedRootAttribute(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The item statement is not a root statement. ({} <Ln 2, Col 20 -> Ln 2, Col 33>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            item: String { root: "value" }
                        """,
                    ),
                    [
                        self.__class__.root_attribute,
                    ],
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootNestedAttribute(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The item statement is not a nested statement. ({} <Ln 1, Col 16 -> Ln 1, Col 25>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { nested: 1 }
                        """,
                    ),
                    [
                        self.__class__.nested_attribute,
                    ],
                )

    # ----------------------------------------------------------------------
    class TestStructure(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="root",
                flags=MetadataAttribute.Flag.Structure | MetadataAttribute.Flag.Root,
            ),
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="nested",
                flags=MetadataAttribute.Flag.Structure | MetadataAttribute.Flag.Nested,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    Structure ->
                        Nested ->
                            pass
                        { nested: 100 }
                    { root: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_ErrorWrongType(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a structure statement. ({} <Ln 1, Col 16 -> Ln 1, Col 23>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRoot(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The structure statement is not a nested statement. ({} <Ln 3, Col 3 -> Ln 3, Col 14>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            pass
                        { nested: 100 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNested(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The structure statement is not a root statement. ({} <Ln 4, Col 7 -> Ln 4, Col 14>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            Nested ->
                                pass
                            { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestType(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="root",
                flags=MetadataAttribute.Flag.Type | MetadataAttribute.Flag.Root,
            ),
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="nested",
                flags=MetadataAttribute.Flag.Type | MetadataAttribute.Flag.Nested,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    Type1: String { root: 1 }

                    Structure ->
                        Type2: String { nested: 100 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_ErrorWrongType(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a type statement. ({} <Ln 1, Col 16 -> Ln 1, Col 23>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNested(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The type statement is not a root statement. ({} <Ln 2, Col 20 -> Ln 2, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            Type: String { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRoot(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The type statement is not a nested statement. ({} <Ln 1, Col 16 -> Ln 1, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Type: String { nested: 100 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestBase(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="root",
                flags=MetadataAttribute.Flag.BaseType | MetadataAttribute.Flag.Root,

            ),
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="nested",
                flags=MetadataAttribute.Flag.BaseType | MetadataAttribute.Flag.Nested,

            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    Structure: String { root: 1 } ->
                        Nested: String { nested: 2 } ->
                            pass
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_ErrorWrongType(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The element is not a base type. ({} <Ln 1, Col 16 -> Ln 1, Col 23>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { root: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorRootAtNested(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'root' is not valid in this context: The type is not a base type. ({} <Ln 2, Col 22 -> Ln 2, Col 29>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure ->
                            Nested: String { root: 1 } ->
                                pass
                        """,
                    ),
                    self.__class__.attributes,
                )

        # ----------------------------------------------------------------------
        def test_ErrorNestedAtRoot(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'nested' is not valid in this context: The type is not a nested type. ({} <Ln 1, Col 21 -> Ln 1, Col 32>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        Structure: String { nested: 100 } ->
                            pass
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    def test_ComboAttribute(self):
        _Test(
            textwrap.dedent(
                """\
                Type: String { attr: 1 }

                Structure: String { attr: 2 } ->
                    pass
                """,
            ),
            [
                _CreateAttribute(
                    IntegerType(Range.CreateFromCode()),
                    name="attr",
                    flags=MetadataAttribute.Flag.Type | MetadataAttribute.Flag.BaseType,
                ),
            ],
        )

    # ----------------------------------------------------------------------
    class TestSingle(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                flags=MetadataAttribute.Flag.SingleCardinality,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    item: String { integer: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_Error(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'integer' is not valid in this context: The type is not a single type. ({} <Ln 1, Col 17 -> Ln 1, Col 27>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String? { integer: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestOptional(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                flags=MetadataAttribute.Flag.OptionalCardinality,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    item: String? { integer: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_Error(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'integer' is not valid in this context: The type is not an optional type. ({} <Ln 1, Col 16 -> Ln 1, Col 26>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { integer: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestContainer(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                flags=MetadataAttribute.Flag.ContainerCardinality,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    item: String[1, 10] { integer: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_Error(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'integer' is not valid in this context: The type is not a container type. ({} <Ln 1, Col 16 -> Ln 1, Col 26>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { integer: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestZeroOrMore(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                flags=MetadataAttribute.Flag.ZeroOrMoreCardinality,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    items: String* { integer: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_Error(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'integer' is not valid in this context: The type is not a zero-or-more container type. ({} <Ln 1, Col 16 -> Ln 1, Col 26>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { integer: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestTestOneOrMore(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                flags=MetadataAttribute.Flag.OneOrMoreCardinality,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    items: String+ { integer: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_Error(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'integer' is not valid in this context: The type is not a one-or-more container type. ({} <Ln 1, Col 16 -> Ln 1, Col 26>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { integer: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    class TestFixed(object):
        attributes                          = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                flags=MetadataAttribute.Flag.FixedContainerCardinality,
            ),
        ]

        # ----------------------------------------------------------------------
        def test_Standard(self):
            _Test(
                textwrap.dedent(
                    """\
                    items: String[3] { integer: 1 }
                    """,
                ),
                self.__class__.attributes,
            )

        # ----------------------------------------------------------------------
        def test_Error(self):
            with pytest.raises(
                SimpleSchemaException,
                match=re.escape("The metadata item 'integer' is not valid in this context: The type is not a fixed-size container type. ({} <Ln 1, Col 16 -> Ln 1, Col 26>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
            ):
                _Test(
                    textwrap.dedent(
                        """\
                        item: String { integer: 1 }
                        """,
                    ),
                    self.__class__.attributes,
                )

    # ----------------------------------------------------------------------
    def test_ComboCardinality(self):
        _Test(
            textwrap.dedent(
                """\
                item: String { integer: 1 }
                item: String[3] { integer: 2 }
                """,
            ),
            [
                _CreateAttribute(
                    IntegerType(Range.CreateFromCode()),
                    flags=MetadataAttribute.Flag.SingleCardinality | MetadataAttribute.Flag.FixedContainerCardinality,
                ),
            ],
        )

    # ----------------------------------------------------------------------
    def test_RequiredMetadata(self):
        attributes = [
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="required1",
                cardinality=Cardinality.CreateFromCode(1, 1),
            ),
            _CreateAttribute(
                IntegerType(Range.CreateFromCode()),
                name="required2",
                cardinality=Cardinality.CreateFromCode(1, 1),
            ),
        ]

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The metadata item 'required2' is required. ({} <Ln 1, Col 14 -> Ln 3, Col 2>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    item: String {
                        required1: 1
                    }
                    """,
                ),
                attributes,
            )

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The metadata item 'required1' is required. ({} <Ln 1, Col 7 -> Ln 1, Col 13>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    item: String
                    """,
                ),
                attributes,
            )

    # ----------------------------------------------------------------------
    def test_WrongType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    A 'int' value cannot be converted to a 'String' type.

                        - {entry_point} <Ln 1, Col 22 -> Ln 1, Col 23>
                        - {name_metadata_attribute_file} <Ln 48, Col 48 -> Ln 48, Col 48>
                        - {entry_point} <Ln 1, Col 16 -> Ln 1, Col 23>
                    """,
                ).format(
                    entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
                    name_metadata_attribute_file=inspect.getmodule(NameMetadataAttribute).__file__,  # type: ignore
                )),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    item: String { name: 2 }
                    """,
                ),
                [
                    NameMetadataAttribute(),
                ],
            )

    # ----------------------------------------------------------------------
    def test_InheritedMetadata(self):
        _Test(
            textwrap.dedent(
                """\
                Type1: String {
                    inheritable: "Type1"
                    standard: "Standard1"
                }

                Type2: Type1
                Type3: Type2

                Type4: Type3 {
                    inheritable: "Type4"
                    standard: "Standard4"
                }
                """,
            ),
            [
                _CreateAttribute(
                    StringType(Range.CreateFromCode()),
                    name="inheritable",
                    flags=MetadataAttribute.Flag.Inheritable,
                ),
                _CreateAttribute(
                    StringType(Range.CreateFromCode()),
                    name="standard",
                ),
            ],
        )


# ----------------------------------------------------------------------
def test_Recursive():
    _Test(
        textwrap.dedent(
            """\
            Directory: String ->
                files: String*
                directories: Directory*

            root: Directory
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_PseudoElement():
    _Test(
        textwrap.dedent(
            """\
            structure ->
                value1: String

            structures ->
                value2: Number
            +

            optional_structure ->
                value3: Date
            ?
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_DisableUnusedRootElement():
    _Test(
        textwrap.dedent(
            """\
            _NeverUsed ->
                pass

            Used ->
                pass
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_DisableElementUsedFromUnused():
    _Test(
        textwrap.dedent(
            """\
            MaybeUsed ->
                # This should not disappear because it is part of a public type
                Type: String

            _Unused ->
                value: MaybeUsed.Type
            """,
        ),
    )


# ----------------------------------------------------------------------
class TestCollapse(object):
    # ----------------------------------------------------------------------
    def test_MultipleBasic(self):
        _Test(
            textwrap.dedent(
                """\
                value: String[3] { min_length: 2 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_MultipleOptional(self):
        _Test(
            textwrap.dedent(
                """\
                value: String? { min_length: 10 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_MultipleStructure(self):
        _Test(
            textwrap.dedent(
                """\
                values ->
                    item: String
                [4]
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_PrivateRootTypedefs(self):
        _Test(
            textwrap.dedent(
                """\
                _Private: String[10]
                _Unused: String[10]

                value: _Private
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_NoCollapseWhenRoot(self):
        _Test(
            textwrap.dedent(
                """\
                Strings: String[10] { min_length: 123 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_CollapseWhenPrivate(self):
        _Test(
            textwrap.dedent(
                """\
                Structure ->
                    _Private: String[10]
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_NoCollapseWhenPublic(self):
        _Test(
            textwrap.dedent(
                """\
                Structure ->
                    Public: String[10]
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_NoCollapseWhenProtected(self):
        _Test(
            textwrap.dedent(
                """\
                Structure ->
                    @Protected: String[10]
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_NoCollapseWhenShared(self):
        _Test(
            textwrap.dedent(
                """\
                _Private: String[10]
                Public: _Private
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_TupleShared(self):
        _Test(
            textwrap.dedent(
                """\
                Strings: String[10]

                Tuple: (Strings, )
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Tuple(self):
        _Test(
            textwrap.dedent(
                """\
                Tuple: (String[10], )
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Variant(self):
        _Test(
            textwrap.dedent(
                """\
                Variant: (Integer | String[10])
                """,
            ),
        )


# ----------------------------------------------------------------------
def test_ItemReference():
    _Test(
        textwrap.dedent(
            """\
            Container: String+ { min_length: 10 }
            ContainerAlias: Container
            Containers: Container+
            """,
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
_default_flags: NormalizeFlag               = (
    NormalizeFlag.AllowRootItems
    | NormalizeFlag.AllowRootStructures
    | NormalizeFlag.AllowRootTypes
    | NormalizeFlag.AllowNestedItems
    | NormalizeFlag.AllowNestedStructures
    | NormalizeFlag.AllowNestedTypes
)


# ----------------------------------------------------------------------
def _TestEx(
    content: dict[str, str],
    entry_points: list[str],
    metadata_attributes: Optional[list[MetadataAttribute]]=None,
    supported_extension_names: Optional[set[str]]=None,
    flags: NormalizeFlag=_default_flags,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[
    Union[
        dict[Path, RootStatement],
        dict[Path, Exception],
    ],
    str,
]:
    with TestHelpers.GenerateMockedPath(content, entry_points) as workspaces:
        dm_and_sink = iter(GenerateDoneManagerAndSink())

        results = Parse(
            cast(DoneManager, next(dm_and_sink)),
            workspaces,
            single_threaded=single_threaded,
            quiet=quiet,
            raise_if_single_exception=raise_if_single_exception,
        )

        assert len(results) == 1, results
        workspace_root, results = next(iter(results.items()))

        assert all(isinstance(value, RootStatement) for value in results.values())
        results = cast(dict[Path, RootStatement], results)

        results = {
            workspace_root / key: value for key, value in results.items()
        }

    dm_and_sink = iter(GenerateDoneManagerAndSink())

    resolve_results = Resolve(
        cast(DoneManager, next(dm_and_sink)),
        results,
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert resolve_results is None

    dm_and_sink = iter(GenerateDoneManagerAndSink())

    normalize_results = Normalize(
        cast(DoneManager, next(dm_and_sink)),
        results,
        metadata_attributes or [],
        supported_extension_names or set(),
        flags,
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    output = cast(str, next(dm_and_sink))

    if normalize_results is not None:
        assert all(isinstance(value, Exception) for value in normalize_results.values())
        return cast(dict[Path, Exception], normalize_results), output

    return cast(dict[Path, RootStatement], results), output


# ----------------------------------------------------------------------
def _RootToYaml(
    root: RootStatement,
) -> str:
    return TestHelpers.ScrubString(TestHelpers.ToYamlString(TestHelpers.ToDict(root)))


# ----------------------------------------------------------------------
def _Test(
    content: str,
    metadata_attributes: Optional[list[MetadataAttribute]]=None,
    supported_extension_names: Optional[set[str]]=None,
    flags: NormalizeFlag=_default_flags,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> str:
    results, output = _TestEx(
        {
            "entry_point": content,
        },
        ["entry_point", ],
        metadata_attributes,
        supported_extension_names,
        flags,
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert not any(isinstance(value, Exception) for value in results.values())

    assert len(results) == 1
    results = next(iter(results.values()))

    assert isinstance(results, RootStatement), results
    TestHelpers.CompareResultsFromFile(
        _RootToYaml(results),
        call_stack_offset=1,
    )

    return output
