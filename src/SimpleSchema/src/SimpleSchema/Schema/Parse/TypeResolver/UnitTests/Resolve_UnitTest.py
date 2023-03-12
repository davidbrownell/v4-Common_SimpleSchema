# ----------------------------------------------------------------------
# |
# |  Resolve_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 12:56:46
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
Unit tests for Resolve.py

Note that these tests are actually Integration tests (as they are using more than one
class or function), but are named "UnitTests" to ensure that they participate in code
coverage collection and enforcement.
"""

import re
import sys
import textwrap

from pathlib import Path
from typing import cast, Optional, Tuple, Union

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
    from SimpleSchema.Schema.Parse import TestHelpers
    from SimpleSchema.Schema.Parse.ANTLR.Parse import Parse
    from SimpleSchema.Schema.Parse.TypeResolver.Resolve import Resolve


# code_coverage: include = ../Resolve.py
# code_coverage: include = ../Impl/Namespace.py
# code_coverage: include = ../Impl/TypeFactories.py


# ----------------------------------------------------------------------
class TestFundamentalTypes(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        _Test(
            textwrap.dedent(
                """\
                boolean: Boolean
                datetime: DateTime
                date: Date
                directory: Directory
                duration: Duration
                enum: Enum { values: ["a", "b", "c"] }
                filename: Filename
                guid: Guid
                integer: Integer
                number: Number
                string: String
                uri: Uri
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_DirectoryCustomizations(self):
        _Test(
            textwrap.dedent(
                """\
                standard: Directory
                no_ensure_exists: Directory { ensure_exists: no }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_EnumCustomizations(self):
        _Test(
            textwrap.dedent(
                """\
                standard: Enum { values: ["a", "b", "c"] }
                starting_value: Enum { values: ["a", "b", "c"], starting_value: 10 }
                int_values: Enum { values: [1, 2, 3] }
                tuple_values: Enum { values: [("a", "A"), ("b", "B"), ("c", "C")] }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_FilenameCustomizations(self):
        _Test(
            textwrap.dedent(
                """\
                standard: Filename
                no_ensure_exists: Filename { ensure_exists: false }
                match_any: Filename { match_any: true }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_IntegerCustomizations(self):
        _Test(
            textwrap.dedent(
                """\
                standard: Integer
                with_min: Integer { min: 10 }
                with_max: Integer { max: 20 }
                with_min_and_max: Integer { min: 10, max: 20 }
                bits: Integer { bits: "Value64" }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorIntegerCustomization(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("100 > 1 ({} <Ln 1, Col 22 -> Ln 1, Col 42>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    invalid_max: Integer { min: 100, max: 1 }
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_NumberCustomizations(self):
        _Test(
            textwrap.dedent(
                """\
                standard: Number
                with_min: Number { min: 10.0 }
                with_max: Number { max: 20.0 }
                with_min_and_max: Number { max: 20.0, min: 10.0 }
                bits: Number { bits: "Value32" }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorNumberCustomization(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'does not exist' is not a valid enum value. ({} <Ln 1, Col 30 -> Ln 1, Col 46>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    invalid_bits: Number { bits: "does not exist" }
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_StringCustomizations(self):
        _Test(
            textwrap.dedent(
                """\
                standard: String
                with_min: String { min_length: 0 }
                with_max: String { max_length: 100 }
                with_min_and_max: String { min_length: 10, max_length: 20 }
                with_expression: String { validation_expression: "foo" }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorStringCustomization(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("missing ), unterminated subpattern at position 0 ({} <Ln 1, Col 28 -> Ln 1, Col 65>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    invalid_expression: String { validation_expression: "(?P<foo>" }
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidItemReference(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Item references to fundamental types are not valid (as they are already item references). ({} <Ln 1, Col 13 -> Ln 1, Col 19>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    type: String::item
                    """,
                ),
            )


# ----------------------------------------------------------------------
def test_TupleAndVariants():
    _Test(
        textwrap.dedent(
            """\
            tuple: (String, Number)
            variant: (String | Number)
            """,
        ),
    )


# ----------------------------------------------------------------------
class TestTypedef(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        _Test(
            textwrap.dedent(
                """\
                Typedef1: String { min_length: 4 }
                Typedef2: Typedef1
                Typedef3: Typedef2

                AddMax1: Typedef1 { max_length: 10 }
                AddMax2: Typedef2 { max_length: 11 }
                AddMax3: Typedef3 { max_length: 12 }

                AddMaxWithMetadata1: Typedef1 { max_length: 10, generic: 20 }
                AddMaxWithMetadata2: Typedef2 { max_length: 11, generic: 21 }
                AddMaxWithMetadata3: Typedef3 { max_length: 12, generic: 22 }

                AddValidation: AddMax1 { validation_expression: "foo" }
                AddValidationWithMetadata: AddMaxWithMetadata1 { validation_expression: "bar", generic2: 200 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Cardinality(self):
        _Test(
            textwrap.dedent(
                """\
                Typedef: String { min_length: 2 }

                Array: Typedef+
                ArrayOfArrays: Array*
                ArrayOfArraysOfArrays: ArrayOfArrays[10]

                Optional: Typedef?
                Optional2: Optional

                # In the following typedefs, the metadata should stick with the typedef
                # (rather than apply to the underlying type), as the referenced
                # type is a container.
                ContainerWithMetadata: Array { min_length: 10 }
                ContainerOfContainersWithMetadata: ArrayOfArrays { min_length: 10 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ItemReference(self):
        _Test(
            textwrap.dedent(
                """\
                Container: String+ { min_length: 10, custom_value: "10" }

                Container1: Container
                ContainerItem: Container::item
                ContainerItemWithMods: Container::item[2] { custom_value: "2" }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorItemReferenceStructure(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    The type 'Structure' is not a container or optional and cannot be used with an item reference.

                        - {entry_point} <Ln 4, Col 30 -> Ln 4, Col 36>
                        - {entry_point} <Ln 1, Col 1 -> Ln 3, Col 1>
                    """,
                ).format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point"),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Structure ->
                        pass

                    bad_structure_item: Structure::item
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorItemReferenceOnSingleItem(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    The type 'SingleItem' is not a container or optional and cannot be used with an item reference.

                        - {entry_point} <Ln 3, Col 21 -> Ln 3, Col 27>
                        - {entry_point} <Ln 1, Col 1 -> Ln 3, Col 1>
                    """,
                ).format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point"),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    SingleItem: String

                    bad_item: SingleItem::item
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_NestedReferences(self):
        _Test(
            textwrap.dedent(
                """\
                One ->
                    Two ->
                        Three ->
                            value: Four.Five

                    Four ->
                        Five ->
                            pass

                three: One.Two.Three
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The type 'DoesNotExist' was not found. ({} <Ln 1, Col 10 -> Ln 1, Col 22>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Typedef: DoesNotExist

                    value: Typedef
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorNestedTypedef(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The type 'Nested' was not found. ({} <Ln 3, Col 16 -> Ln 3, Col 22>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Typedef: String

                    value: Typedef.Nested
                    """,
                ),
            )


# ----------------------------------------------------------------------
class TestStructure(object):
    # ----------------------------------------------------------------------
    def test_Simple(self):
        _Test(
            textwrap.dedent(
                """\
                EmptyStructure ->
                    pass

                empty: EmptyStructure

                SimpleStructure ->
                    value1: String
                    value2: Integer

                simple: SimpleStructure
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Bases(self):
        _Test(
            textwrap.dedent(
                """\
                Simple: String { min_length: 2 } ->
                    value1: Number

                Derived1: Simple ->
                    pass

                Derived2: Simple ->
                    value2: String

                MultiBase: Derived1, Derived2 ->
                    value3: Boolean

                simple: Simple
                derived1: Derived1
                derived2: Derived2
                multi_base: MultiBase

                applied_cardinality: MultiBase*
                applied_metadata: MultiBase { new_value: 10 }
                applied_cardinality_and_metadata: MultiBase* { new_value: 10 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Metadata(self):
        _Test(
            textwrap.dedent(
                """\
                Metadata ->
                    pass
                { custom_value: 10 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorCircularStructureDef(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    A cycle was detected in the definition of 'One':

                        * 'One' {entry_point} <Ln 1, Col 1 -> Ln 1, Col 4>
                        * 'Base type 'Two' (index 0)' {entry_point} <Ln 1, Col 6 -> Ln 1, Col 9>
                        * 'Two' {entry_point} <Ln 4, Col 1 -> Ln 4, Col 4>
                        * 'Base type 'Three' (index 0)' {entry_point} <Ln 4, Col 6 -> Ln 4, Col 11>
                        * 'Three' {entry_point} <Ln 7, Col 1 -> Ln 7, Col 6>
                        * 'Base type 'One' (index 0)' {entry_point} <Ln 7, Col 8 -> Ln 7, Col 11>
                        * 'One' {entry_point} <Ln 1, Col 1 -> Ln 1, Col 4>

                        - {entry_point} <Ln 1, Col 1 -> Ln 1, Col 4>
                    """,
                ).format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point"),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    One: Two ->
                        pass

                    Two: Three, String ->
                        pass

                    Three: One ->
                        pass
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_PseudoStructures(self):
        _Test(
            textwrap.dedent(
                """\
                simple ->
                    value1: String
                    value2: Number

                with_base: String ->
                    value1: String

                with_metadata ->
                    value1: String
                {
                    custom_value1: 10
                }

                with_cardinality ->
                    value1: Boolean
                *

                everything: String ->
                    value1: Boolean
                ?
                {
                    custom_value1: 10
                    custom_value2: 20
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorEmptyPseudoStructure(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Pseudo structure definitions must contain at least one child. ({} <Ln 1, Col 1 -> Ln 3, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    foo ->
                        pass
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_Nested(self):
        _Test(
            textwrap.dedent(
                """\
                Person ->
                    child ->
                        value1: String

                        grandchild ->
                            value2: Number

                        value3: Boolean

                    value4: Boolean

                person: Person+
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_SelfReference(self):
        _Test(
            textwrap.dedent(
                """\
                Directory ->
                    name: String

                    files: String+
                    directories: Directory*

                file_system: Directory*
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateSiblingType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                "The type 'Type' has already been defined at '{filename} <Ln 1, Col 1 -> Ln 1, Col 5>'. ({filename} <Ln 3, Col 1 -> Ln 3, Col 5>)".format(
                    filename=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
                ),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Type: String

                    Type ->
                        pass
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateAncestorType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                "The type 'Type' has already been defined at '{filename} <Ln 1, Col 1 -> Ln 1, Col 5>'. ({filename} <Ln 4, Col 13 -> Ln 4, Col 17>)".format(
                    filename=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
                ),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    Type ->
                        One ->
                            Two ->
                                Type: String
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateElderType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                "The type 'Type' has already been defined at '{filename} <Ln 2, Col 5 -> Ln 2, Col 9>'. ({filename} <Ln 7, Col 17 -> Ln 7, Col 21>)".format(
                    filename=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
                ),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    One ->
                        Type: Number

                        Two ->
                            Three ->
                                Four ->
                                    Type: String
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidNested(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The type 'DoesNotExist' was not found. ({} <Ln 7, Col 22 -> Ln 7, Col 34>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    One ->
                        Two ->
                            Three ->
                                Four ->
                                    pass

                    value: One.Two.Three.DoesNotExist
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidBaseCardinality(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    Base types must have a cardinality of 1.

                        - {entry_point} <Ln 4, Col 9 -> Ln 4, Col 16>
                        - {entry_point} <Ln 1, Col 1 -> Ln 2, Col 1>
                        - {entry_point} <Ln 2, Col 1 -> Ln 4, Col 1>
                    """,
                ).format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point"),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    InvalidBase: String+
                    Typedef: InvalidBase

                    Struct: Typedef ->
                        pass
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidBaseType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    Base types must be structure- or fundamental-types.

                        - {entry_point} <Ln 3, Col 9 -> Ln 3, Col 20>
                        - {entry_point} <Ln 1, Col 1 -> Ln 3, Col 1>
                    """,
                ).format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point"),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    InvalidBase: (String | Integer)

                    Struct: InvalidBase ->
                        pass
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidMultipleBaseType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    Base types must be structure types when multiple base types are specified.

                        - {entry_point} <Ln 8, Col 17 -> Ln 8, Col 22>
                        - {entry_point} <Ln 1, Col 1 -> Ln 3, Col 1>
                        - {entry_point} <Ln 6, Col 1 -> Ln 8, Col 1>
                    """,
                ).format(entry_point=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point"),
            ),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    StringType: String

                    Base1 ->
                        pass

                    Base2: StringType

                    Derived: Base1, Base2 ->
                        pass
                    """,
                ),
            )


# ----------------------------------------------------------------------
class TestIncludes(object):
    # ----------------------------------------------------------------------
    def test_Named(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from Foo import Bar, Baz as Baz_

                    bar: Bar
                    baz: Baz_
                    """,
                ),
                "Foo.SimpleSchema": textwrap.dedent(
                    """\
                    Bar ->
                        value: String

                    Baz ->
                        value: Number
                    """,
                ),
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_Star(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from Foo import *

                    bar: Bar
                    baz: Baz
                    """,
                ),
                "Foo.SimpleSchema": textwrap.dedent(
                    """\
                    Bar ->
                        value: String

                    Baz ->
                        value: Number
                    """,
                ),
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_Module(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    import Foo

                    bar: Foo.Bar
                    baz: Foo.Baz
                    """,
                ),
                "Foo.SimpleSchema": textwrap.dedent(
                    """\
                    Bar ->
                        value: String

                    Baz ->
                        value: Number
                    """,
                ),
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_ImportTypedef(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from included import Type

                    type: Type
                    """,
                ),
                "included": "Type: String { min_length: 2 }",
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_ErrorImportInvalidType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The included item 'ThisTypeDoesNotExist' does not exist. ({} <Ln 1, Col 22 -> Ln 1, Col 42>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _TestEx(
                {
                    "entry_point": "from included import ThisTypeDoesNotExist",
                    "included": "",
                },
            )

    # ----------------------------------------------------------------------
    def test_PrivatesAreSkippedNamed(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The included item '_Baz' exists but is not accessible due to its visibility. ({} <Ln 1, Col 32 -> Ln 1, Col 36>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _TestEx(
                {
                    "entry_point": textwrap.dedent(
                        """\
                        from included import Foo, Bar, _Baz
                        """,
                    ),
                    "included": textwrap.dedent(
                        """\
                        Foo: String ->
                            pass

                        Bar: Number ->
                            pass

                        _Baz: Boolean ->
                            pass
                        """,
                    ),
                },
            )

    # ----------------------------------------------------------------------
    def test_PrivatesAreSkippedModule(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The type '_Baz' was not found. ({} <Ln 6, Col 33 -> Ln 6, Col 37>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _TestEx(
                {
                    "entry_point": textwrap.dedent(
                        """\
                        import Included

                        foo: Included.Foo
                        bar: Included.Bar

                        this_will_be_an_error: Included._Baz
                        """,
                    ),
                    "Included": textwrap.dedent(
                        """\
                        Foo: String ->
                            pass

                        Bar: Number

                        _Baz: Boolean ->
                            pass
                        """,
                    ),
                },
            )

    # ----------------------------------------------------------------------
    def test_ErrorCircularDefinitionAcrossImports(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from included import Two

                    One: Two ->
                        pass

                    Three: One ->
                        pass
                    """,
                ),

                "included": textwrap.dedent(
                    """\
                    from entry_point import Three

                    Two: Three ->
                        pass
                    """,
                ),
            },
        )[0]

        assert len(results) == 2
        assert all(isinstance(result, Exception) for result in results.values())

        results = list(results.values())

        expected_error = textwrap.dedent(
            """\
            A cycle was detected in the definition of 'One':

                * 'One' {entry_point_filename} <Ln 3, Col 1 -> Ln 3, Col 4>
                * 'Base type 'Two' (index 0)' {entry_point_filename} <Ln 3, Col 6 -> Ln 3, Col 9>
                * 'Two' {included_filename} <Ln 3, Col 1 -> Ln 3, Col 4>
                * 'Base type 'Three' (index 0)' {included_filename} <Ln 3, Col 6 -> Ln 3, Col 11>
                * 'Three' {entry_point_filename} <Ln 6, Col 1 -> Ln 6, Col 6>
                * 'Base type 'One' (index 0)' {entry_point_filename} <Ln 6, Col 8 -> Ln 6, Col 11>
                * 'One' {entry_point_filename} <Ln 3, Col 1 -> Ln 3, Col 4>

                - {entry_point_filename} <Ln 3, Col 1 -> Ln 3, Col 4>
            """,
        ).format(
            entry_point_filename=TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
            included_filename=TestHelpers.DEFAULT_WORKSPACE_PATH / "included",
        )

        assert str(results[0]) == expected_error
        assert str(results[1]) == expected_error

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _DictToString(
        results: Union[dict[Path, RootStatement], dict[Path, Exception]]
    ) -> str:
        assert not any(isinstance(value, Exception) for value in results.values())

        return TestHelpers.ScrubString(
            TestHelpers.ToYamlString(
                {
                    str(key): TestHelpers.ToDict(cast(RootStatement, value))
                    for key, value in results.items()
                },
            ),
        )


# ----------------------------------------------------------------------
class TestRootProtectedErrors(object):
    # ----------------------------------------------------------------------
    def test_Item(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The visibility 'protected' is not valid for root elements. ({} <Ln 1, Col 1 -> Ln 1, Col 2>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    @protected_item: String
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_Structure(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The visibility 'protected' is not valid for root elements. ({} <Ln 1, Col 1 -> Ln 1, Col 2>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    @ProtectedStructure ->
                        pass
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_Type(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The visibility 'protected' is not valid for root elements. ({} <Ln 1, Col 1 -> Ln 1, Col 2>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    @Type: String
                    """,
                ),
            )


# ----------------------------------------------------------------------
def test_OutOfOrderStatements():
    _Test(
        textwrap.dedent(
            """\
            inner_type: DefinedLater.InnerType

            DefinedLater ->
                _PrivateType: String
                InnerType: _PrivateType
            """,
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _TestEx(
    content: dict[str, str],
    entry_points: Optional[list[str]]=None,
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
    if entry_points is None:
        assert "entry_point" in content
        entry_points = ["entry_point", ]

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

        results = {
            workspace_root / key: value for key, value in results.items()
        }

        assert all(isinstance(value, RootStatement) for value in results.values())
        results = cast(dict[Path, RootStatement], results)

    dm_and_sink = iter(GenerateDoneManagerAndSink())

    resolve_results = Resolve(
        cast(DoneManager, next(dm_and_sink)),
        results,
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    output = cast(str, next(dm_and_sink))

    return resolve_results or results, output


# ----------------------------------------------------------------------
def _RootToYaml(
    root: RootStatement,
) -> str:
    return TestHelpers.ScrubString(TestHelpers.ToYamlString(TestHelpers.ToDict(root)))


# ----------------------------------------------------------------------
def _Test(
    content: str,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> str:
    results, output = _TestEx(
        {
            "entry_point": content,
        },
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
