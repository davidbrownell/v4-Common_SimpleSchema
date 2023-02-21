# ----------------------------------------------------------------------
# |
# |  Parse_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 13:13:45
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
Unit tests for Parse.py

Note that these tests are actually Integration tests (as they are using more than once
class or function), but named UnitTests to ensure that they participate in code coverage
collection and enforcement.
"""

import re
import sys
import textwrap

from pathlib import Path
from typing import cast, Optional, Tuple

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
    from SimpleSchema.Schema.Parse.ANTLR.Parse import Parse, AntlrException


# ----------------------------------------------------------------------
class TestMetadata(object):
    # ----------------------------------------------------------------------
    def test_Empty(self):
        _Test(
            textwrap.dedent(
                """\
                empty1: String { pass }
                empty2: String {
                    pass
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_SingleItem(self):
        _Test(
            textwrap.dedent(
                """\
                single1: String { value1: 1 }
                single2: String { value2: 2, }
                single3: String {
                    value3: 3
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_MultipleItems(self):
        _Test(
            textwrap.dedent(
                """\
                multiple1: String { value1a: 1, value1b: 10 }
                multiple2: String { value2a: 2, value2b: 20, }
                multiple3: String {
                    value3a: 3
                    value3b: 30
                    value3c: 300
                }
                """,
            ),
        )


# ----------------------------------------------------------------------
def test_Cardinality():
    _Test(
        textwrap.dedent(
            """\
            single: String
            optional: String?
            zero_or_more: String*
            one_or_more: String+
            fixed: String[3]
            range: String[2, 10]
            with_metadata: String? { default: "Foo" }
            """,
        ),
    )


# ----------------------------------------------------------------------
class TestExpressionTypes(object):
    # ----------------------------------------------------------------------
    def test_General(self):
        _Test(
            textwrap.dedent(
                """\
                value: String {
                    number: 1.234
                    negative_number: -4.56
                    integer: 56
                    negative_integer: -1
                    none: None
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_True(self):
        _Test(
            textwrap.dedent(
                """\
                value: String {
                    value1: y
                    value2: Y
                    value3: yes
                    value4: Yes
                    value5: YES
                    value6: true
                    value7: True
                    value8: TRUE
                    value9: on
                    value10: On
                    value11: ON
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_False(self):
        _Test(
            textwrap.dedent(
                """\
                value: String {
                    value1: n
                    value2: N
                    value3: no
                    value4: No
                    value5: NO
                    value6: false
                    value7: False
                    value8: FALSE
                    value9: off
                    value10: Off
                    value11: OFF
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Strings(self):
        _Test(
            textwrap.dedent(
                """\
                value: String {{
                    value1: "The \\"Test\\""
                    value2: 'Another \\'Test\\''
                    value3: {triple_quote}
                            A
                                multiline

                            string.
                            {triple_quote}
                    value4: '''
                            More multiline
                              strings
                            on

                                different

                            lines.
                            '''
                }}
                """,
            ).format(triple_quote='"""'),
        )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidOpeningToken(self):
        with pytest.raises(
            Exception,
            match=re.escape("Triple-quote delimiters that initiate multiline strings cannot have any content on the same line. ({} <Ln 2, Col 15>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    value: String {
                        value: '''invalid
                               String
                               '''
                    }
                    """,
                ),
                quiet=True,
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidClosingToken(self):
        with pytest.raises(
            Exception,
            match=re.escape("Triple-quote delimiters that terminate multiline strings cannot have any content on the same line. ({} <Ln 4, Col 12>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    value: String {
                        value: '''
                               Valid
                               invalid'''
                    }
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidWhitespace(self):
        with pytest.raises(
            Exception,
            match=re.escape("Invalid multiline string indentation. ({} <Ln 4, Col 9>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    value: String {
                        value: '''
                               Valid line 1
                            Invalid line
                               Valid line 2
                               '''
                    }
                    """,
                ),
            )

    # ----------------------------------------------------------------------
    def test_List(self):
        _Test(
            textwrap.dedent(
                """\
                value: String {
                    value1: []
                    value2: [1, ]
                    value3: [
                        1
                    ]
                    value4: [
                        1,
                    ]
                    value5: [1, 2, 3, 4, ]
                    value6: [
                        1,
                        2,
                        3,
                        4,
                    ]
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Tuple(self):
        _Test(
            textwrap.dedent(
                """\
                value: String {
                    value1: (1, )
                    value2: (1, 2, 3, 4)
                    value3: (1, 2, 3, 4, 5, )
                }
                """,
            ),
        )


# ----------------------------------------------------------------------
class TestTypes(object):
    # ----------------------------------------------------------------------
    def test_ParseIdentifier(self):
        _Test(
            textwrap.dedent(
                """\
                value1: One.Two.Three
                value2: One::item
                value3: One.Two.Three::item
                value4: ::Global
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Tuples(self):
        _Test(
            textwrap.dedent(
                """\
                value1: (One, )
                value2: (One, Two)
                value3: (One, Two, Three, )
                value4: (One, (Two, Three, (Four, ), ), )
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Variant(self):
        _Test(
            textwrap.dedent(
                """\
                value1: (One | Two)
                value2: (One | Two | Three | Four)
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_WithMetadata(self):
        _Test(
            textwrap.dedent(
                """\
                value1: One { metadata: 1 }
                value2: (One { metadata1: 1 }, ) { metadata2: 2 }
                value3: (One | Two { m2: 2, m3: 3}) { m4: 4 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_WithCardinality(self):
        _Test(
            textwrap.dedent(
                """\
                value1: Type*
                value2: (Type*, )?
                value3: (One? | Two* | Three[3])+
                """,
            ),
        )


# ----------------------------------------------------------------------
def test_ParseItem():
    _Test(
        textwrap.dedent(
            """\
            Uppercase: Type
            lowercase: Type
            @protected: Type
            _private: Type
            """,
        ),
    )


# ----------------------------------------------------------------------
class TestExtensions(object):
    # ----------------------------------------------------------------------
    def test_Empty(self):
        _Test(
            textwrap.dedent(
                """\
                Ext1()
                ext2()
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Positional(self):
        _Test(
            textwrap.dedent(
                """\
                Ext1("one")
                Ext2("one", )
                Ext3("one", 2, 3.14, "four")
                Ext4(
                    "one",
                    2,
                    3.14,
                    "four",
                )
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Keyword(self):
        _Test(
            textwrap.dedent(
                """\
                Ext1(one=1)
                Ext2(one=1, )
                Ext3(one=1, two=2, three=3.14, four="four")
                Ext4(
                    one=1,
                    two=2,
                    three=3.14,
                    four="four",
                )
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_PositionalAndKeyword(self):
        _Test(
            textwrap.dedent(
                """\
                Ext(1, 2, three=3.14, four="four")
                """,
            ),
        )


# ----------------------------------------------------------------------
class TestStructure(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        _Test(
            textwrap.dedent(
                """\
                Simple ->
                    pass

                WithChildren ->
                    one: Two
                    three: Four

                WithBase: Base ->
                    pass

                WithTupleBase: (One, Two, ) ->
                    pass
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_WithMetadata(self):
        _Test(
            textwrap.dedent(
                """\
                Simple ->
                    pass
                {
                    one: 1
                }

                WithBase: Base ->
                    pass
                {
                    one: 1
                    two: 2
                }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_WithCardinality(self):
        _Test(
            textwrap.dedent(
                """\
                Simple ->
                    pass
                *

                WithBase: Base ->
                    pass
                +

                WithBaseAndMetadata: Base ->
                    pass
                ? { one: 1 }
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_Nested(self):
        _Test(
            textwrap.dedent(
                """\
                One ->
                    Two ->
                        pass

                Person ->
                    one: One

                    Child ->
                        Grandchild ->
                            two: Two

                        three: Three

                    four: Four
                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_ErrorVariantBase(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Base types must be an identifier or a tuple that contains identifiers. ({} <Ln 1, Col 19 -> Ln 1, Col 30>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    InvalidStructure: (One | Two) ->
                        pass
                    """,
                ),
                quiet=True,
            )

    # ----------------------------------------------------------------------
    def test_ErrorNestedTupleBase(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Tuple base types may only contain identifiers. ({} <Ln 1, Col 25 -> Ln 1, Col 32>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    InvalidStructure: (One, (Two, )) ->
                        pass
                    """,
                ),
            )


# ----------------------------------------------------------------------
def test_SimpleStructure():
    _Test(
        textwrap.dedent(
            """\
            Simple {
                one: 1
                two: 2
            }
            """,
        ),
    )


# ----------------------------------------------------------------------
class TestInclude(object):
    # ----------------------------------------------------------------------
    def test_Named(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from Foo import Bar
                    from Foo import Bar as Bar_
                    from Foo import Bar,
                    from Foo import Bar, Baz
                    from Foo import (
                        Bar as Bar_,
                        Baz as Baz_,
                    )
                    from Foo.SimpleSchema import Bar
                    """,
                ),
                "Foo.SimpleSchema": "one: Two",
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_Module(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from Subdir import Foo
                    from Subdir/Subdir2 import Bar
                    import Baz
                    """,
                ),
                "Subdir/Foo.SimpleSchema": "one: Two",
                "Subdir/Subdir2/Bar.SimpleSchema": "three: Four",
                "Baz.SimpleSchema": "five: Six",
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_Star(self):
        results = _TestEx(
            {
                "entry_point": textwrap.dedent(
                    """\
                    from Subdir/Foo import *
                    from Bar import *
                    """,
                ),
                "Subdir/Foo.SimpleSchema": "one: Two",
                "Bar.SimpleSchema": "three: Four",
            },
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_ImportParentDir(self):
        results = _TestEx(
            {
                "Subdir1/Subdir2/entry_point.SimpleSchema": textwrap.dedent(
                    """\
                    from ../../Foo import *
                    """,
                ),
                "Foo.SimpleSchema": "one: Two",
            },
            [ "Subdir1/Subdir2/entry_point.SimpleSchema", ],
        )[0]

        TestHelpers.CompareResultsFromFile(self._DictToString(results))

    # ----------------------------------------------------------------------
    def test_ErrorInvalidModule(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'DoesNotExist' is not a valid filename or directory name. ({} <Ln 1, Col 6 -> Ln 1, Col 18>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _TestEx(
                {
                    "entry_point": "from DoesNotExist import *",
                },
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidRoot(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'DoesNotExist' is not a valid filename. ({} <Ln 1, Col 1 -> Ln 1, Col 20>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _TestEx(
                {
                    "entry_point": "import DoesNotExist",
                },
            )

    # ----------------------------------------------------------------------
    def test_ErrorOutsideOfPath(self):
        filename = Path(PathEx.CreateRelativePath(TestHelpers.DEFAULT_WORKSPACE_PATH, PathEx.EnsureFile(TestHelpers.DEFAULT_WORKSPACE_PATH / ".." / "__init__.py")))

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                "The included file '{}' is not a descendant of any workspace. ({} <Ln 1, Col 1 -> Ln 1, Col 29>)".format(
                    (TestHelpers.DEFAULT_WORKSPACE_PATH / filename).resolve(),
                    TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
                ),
            ),
        ):
            _TestEx(
                {
                    "entry_point": "from {} import *".format(filename.as_posix())
                },
            )

    # ----------------------------------------------------------------------
    def test_ErrorDirModuleImportWithMultipleFilenames(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A single filename must be imported when including content from a directory. ({} <Ln 1, Col 25 -> Ln 1, Col 28>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _TestEx(
                {
                    "entry_point": textwrap.dedent(
                        """\
                        from Subdir import Foo, Bar
                        """,
                    ),
                    "Subdir/Foo": "",
                    "Subdir/Bar": "",
                },
            )

    # ----------------------------------------------------------------------
    def test_ErrorWildcardImportFromDir(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                "Filenames must be provided with wildcard imports; '{}' is a directory. ({} <Ln 1, Col 1 -> Ln 2, Col 1>)".format(
                    TestHelpers.DEFAULT_WORKSPACE_PATH / "Subdir",
                    TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point",
                ),
            ),
        ):
            _TestEx(
                {
                    "entry_point": textwrap.dedent(
                        """\
                        from Subdir import *
                        """,
                    ),
                    "Subdir/Foo": "",
                },
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _DictToString(
        results: dict[Path, RootStatement],
    ) -> str:
        return TestHelpers.ScrubString(
            TestHelpers.ToYamlString(
                {
                    str(key): TestHelpers.ToDict(value)
                    for key, value in results.items()
                },
            ),
        )


# ----------------------------------------------------------------------
class TestMisc(object):
    # ----------------------------------------------------------------------
    def test_EmptyFile(self):
        _Test("")

    # ----------------------------------------------------------------------
    def test_OnlyComments(self):
        _Test(
            textwrap.dedent(
                """\
                # This is the only thing in the file



                """,
            ),
        )

    # ----------------------------------------------------------------------
    def test_IndentationWithTabs(self):
        _Test(
            textwrap.dedent(
                '''\
                one: Two {{
                    value1: """
                {tab}{tab}{tab}Hello
                {tab}{tab}{tab}"""
                }}
                '''
            ).format(tab="\t"),
        )

    # ----------------------------------------------------------------------
    def test_EmptyLineWithLinespace(self):
        _Test(
            textwrap.dedent(
                '''
                one: Two {{
                    value:  """
                {tab}{tab}{tab}Hi!
                {tab}{tab}
                {tab}{tab}{tab}"""
                }}
                ''',
            ).format(tab="\t"),
        )

    # ----------------------------------------------------------------------
    def test_SyntaxError(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("mismatched input 'newLine' expecting INDENT ({} <Ln 2, Col 1>)".format(TestHelpers.DEFAULT_WORKSPACE_PATH / "entry_point")),
        ):
            _Test(
                textwrap.dedent(
                    """\
                    InvalidStructure ->
                    """,
                ),
                quiet=True,
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
) -> Tuple[dict[Path, RootStatement], str]:
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

        output = cast(str, next(dm_and_sink))

        assert len(results) == 1
        results = next(iter(results.values()))

        return cast(dict[Path, RootStatement], results), output


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
