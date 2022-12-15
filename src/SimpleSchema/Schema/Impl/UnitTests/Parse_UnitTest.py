# ----------------------------------------------------------------------
# |
# |  Parse_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-12 12:21:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Parse.py"""

import re
import sys
import textwrap

from pathlib import Path
from typing import cast, Dict, List, Tuple, Union
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Parse import (
        AntlrException,
        BooleanExpression,
        CompoundStatement,
        DataMemberStatement,
        Element,
        ExtensionStatement,
        ExtensionStatementKeywordArg,
        IdentifierExpression,
        Identifier,
        IdentifierType,
        IntegerExpression,
        Location,
        MetadataExpression,
        MetadataExpressionItem,
        NoneExpression,
        NumberExpression,
        Parse,
        Range,
        RootStatement,
        SimpleSchemaException,
        Statement,
        StringExpression,
        TupleType,
        VariantType,
    )


# ----------------------------------------------------------------------
class TestSingleDataMemberStatement(object):
    # ----------------------------------------------------------------------
    def test_NoMetadata(self):
        result = _Test(
            textwrap.dedent(
                """\
                foo: String
                """,
            ),
        )[0]

        assert result == [
            DataMemberStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                IdentifierExpression(Range(_single_test_file, Location(1, 1), Location(1, 4)), "foo"),
                IdentifierType(Range(_single_test_file, Location(1, 6), Location(1, 12)), "String"),
                None,
            ),
        ]

    # ----------------------------------------------------------------------
    def test_WithSingleLinePassMetadata(self):
        result = _Test(
            textwrap.dedent(
                """\
                foo: String { pass }
                """,
            ),
        )[0]

        assert result == [
            DataMemberStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                IdentifierExpression(Range(_single_test_file, Location(1, 1), Location(1, 4)), "foo"),
                IdentifierType(Range(_single_test_file, Location(1, 6), Location(1, 12)), "String"),
                MetadataExpression(
                    Range(_single_test_file, Location(1, 13), Location(1, 21)),
                    [],
                ),
            ),
        ]

    # ----------------------------------------------------------------------
    def test_WithMultiLinePassMetadata(self):
        result = _Test(
            textwrap.dedent(
                """\
                foo: String {
                    pass
                }
                """,
            ),
        )[0]

        assert result == [
            DataMemberStatement(
                Range.Create(_single_test_file, 1, 1, 4, 1),
                IdentifierExpression(Range(_single_test_file, Location(1, 1), Location(1, 4)), "foo"),
                IdentifierType(Range(_single_test_file, Location(1, 6), Location(1, 12)), "String"),
                MetadataExpression(
                    Range(_single_test_file, Location(1, 13), Location(3, 2)),
                    [],
                ),
            ),
        ]

    # ----------------------------------------------------------------------
    def test_WithSingleLineMetadata(self):
        result = _Test(
            textwrap.dedent(
                """\
                foo: String { one: 1, two: 20 }
                """,
            ),
        )[0]

        assert result == [
            DataMemberStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                IdentifierExpression(Range(_single_test_file, Location(1, 1), Location(1, 4)), "foo"),
                IdentifierType(Range(_single_test_file, Location(1, 6), Location(1, 12)), "String"),
                MetadataExpression(
                    Range(_single_test_file, Location(1, 13), Location(1, 32)),
                    [
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 1, 15, 1, 21),
                            IdentifierExpression(Range.Create(_single_test_file, 1, 15, 1, 18), "one"),
                            IntegerExpression(Range.Create(_single_test_file, 1, 20, 1, 21), 1),
                        ),
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 1, 23, 1, 30),
                            IdentifierExpression(Range.Create(_single_test_file, 1, 23, 1, 26), "two"),
                            IntegerExpression(Range.Create(_single_test_file, 1, 28, 1, 30), 20),
                        ),
                    ],
                ),
            ),
        ]

    # ----------------------------------------------------------------------
    def test_WithMultiLineMetadata(self):
        result = _Test(
            textwrap.dedent(
                """\
                foo: String {
                    one: 1
                    two: 20
                }
                """,
            ),
        )[0]

        assert result == [
            DataMemberStatement(
                Range.Create(_single_test_file, 1, 1, 5, 1),
                IdentifierExpression(Range(_single_test_file, Location(1, 1), Location(1, 4)), "foo"),
                IdentifierType(Range(_single_test_file, Location(1, 6), Location(1, 12)), "String"),
                MetadataExpression(
                    Range(_single_test_file, Location(1, 13), Location(4, 2)),
                    [
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 2, 5, 2, 11),
                            IdentifierExpression(Range.Create(_single_test_file, 2, 5, 2, 8), "one"),
                            IntegerExpression(Range.Create(_single_test_file, 2, 10, 2, 11), 1),
                        ),
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 3, 5, 3, 12),
                            IdentifierExpression(Range.Create(_single_test_file, 3, 5, 3, 8), "two"),
                            IntegerExpression(Range.Create(_single_test_file, 3, 10, 3, 12), 20),
                        ),
                    ],
                ),
            ),
        ]


# ----------------------------------------------------------------------
def test_ExpressionTypes():
    assert _Test(
        textwrap.dedent(
            """\
            data: String {{
                identifier_value: identifier

                positive_integer: 10
                negative_integer: -200

                positive_number_leading_zero: 0.123
                positive_number: .45
                negative_number: -10.8812

                true_value: true
                yes_value: yes
                false_value: False
                no_value: N

                none_value1: null
                none_value2: ~

                double_quote_string_value: "double quotes"
                single_quote_string_value: 'single quotes'

                double_quote_with_escapes: "double \\"quotes\\""
                single_quote_with_escapes: 'doing \\'more testing\\' today'

                multiline_triple_string: {triple_double_quote}
                                         This is
                                         a
                                             multiline
                                         string!

                                         {triple_double_quote}

                multiline_triple_string_single: '''
                                                And more
                                                    testing
                                                  for
                                                different types.
                                                '''
            }}
            """,
        ).format(triple_double_quote='"""'),
    )[0] == [
        DataMemberStatement(
            Range.Create(_single_test_file, 1, 1, 40, 1),
            IdentifierExpression(Range.Create(_single_test_file, 1, 1, 1, 5), "data"),
            IdentifierType(Range.Create(_single_test_file, 1, 7, 1, 13), "String"),
            MetadataExpression(
                Range.Create(_single_test_file, 1, 14, 39, 2),
                [
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 2, 5, 2, 33),
                        IdentifierExpression(Range.Create(_single_test_file, 2, 5, 2, 21), "identifier_value"),
                        Identifier(Range.Create(_single_test_file, 2, 23, 2, 33), "identifier"),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 4, 5, 4, 25),
                        IdentifierExpression(Range.Create(_single_test_file, 4, 5, 4, 21), "positive_integer"),
                        IntegerExpression(Range.Create(_single_test_file, 4, 23, 4, 25), 10),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 5, 5, 5, 27),
                        IdentifierExpression(Range.Create(_single_test_file, 5, 5, 5, 21), "negative_integer"),
                        IntegerExpression(Range.Create(_single_test_file, 5, 23, 5, 27), -200),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 7, 5, 7, 40),
                        IdentifierExpression(Range.Create(_single_test_file, 7, 5, 7, 33), "positive_number_leading_zero"),
                        NumberExpression(Range.Create(_single_test_file, 7, 35, 7, 40), 0.123),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 8, 5, 8, 25),
                        IdentifierExpression(Range.Create(_single_test_file, 8, 5, 8, 20), "positive_number"),
                        NumberExpression(Range.Create(_single_test_file, 8, 22, 8, 25), 0.45),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 9, 5, 9, 30),
                        IdentifierExpression(Range.Create(_single_test_file, 9, 5, 9, 20), "negative_number"),
                        NumberExpression(Range.Create(_single_test_file, 9, 22, 9, 30), -10.8812),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 11, 5, 11, 21),
                        IdentifierExpression(Range.Create(_single_test_file, 11, 5, 11, 15), "true_value"),
                        BooleanExpression(Range.Create(_single_test_file, 11, 17, 11, 21), True),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 12, 5, 12, 19),
                        IdentifierExpression(Range.Create(_single_test_file, 12, 5, 12, 14), "yes_value"),
                        BooleanExpression(Range.Create(_single_test_file, 12, 16, 12, 19), True),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 13, 5, 13, 23),
                        IdentifierExpression(Range.Create(_single_test_file, 13, 5, 13, 16), "false_value"),
                        BooleanExpression(Range.Create(_single_test_file, 13, 18, 13, 23), False),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 14, 5, 14, 16),
                        IdentifierExpression(Range.Create(_single_test_file, 14, 5, 14, 13), "no_value"),
                        BooleanExpression(Range.Create(_single_test_file, 14, 15, 14, 16), False),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 16, 5, 16, 22),
                        IdentifierExpression(Range.Create(_single_test_file, 16, 5, 16, 16), "none_value1"),
                        NoneExpression(Range.Create(_single_test_file, 16, 18, 16, 22)),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 17, 5, 17, 19),
                        IdentifierExpression(Range.Create(_single_test_file, 17, 5, 17, 16), "none_value2"),
                        NoneExpression(Range.Create(_single_test_file, 17, 18, 17, 19)),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 19, 5, 19, 47),
                        IdentifierExpression(Range.Create(_single_test_file, 19, 5, 19, 30), "double_quote_string_value"),
                        StringExpression(Range.Create(_single_test_file, 19, 32, 19, 47), "double quotes"),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 20, 5, 20, 47),
                        IdentifierExpression(Range.Create(_single_test_file, 20, 5, 20, 30), "single_quote_string_value"),
                        StringExpression(Range.Create(_single_test_file, 20, 32, 20, 47), "single quotes"),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 22, 5, 22, 51),
                        IdentifierExpression(Range.Create(_single_test_file, 22, 5, 22, 30), "double_quote_with_escapes"),
                        StringExpression(Range.Create(_single_test_file, 22, 32, 22, 51), 'double "quotes"'),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 23, 5, 23, 62),
                        IdentifierExpression(Range.Create(_single_test_file, 23, 5, 23, 30), "single_quote_with_escapes"),
                        StringExpression(Range.Create(_single_test_file, 23, 32, 23, 62), "doing 'more testing' today"),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 25, 5, 31, 33),
                        IdentifierExpression(Range.Create(_single_test_file, 25, 5, 25, 28), "multiline_triple_string"),
                        StringExpression(Range.Create(_single_test_file, 25, 30, 31, 33), "This is\na\n    multiline\nstring!\n"),
                    ),
                    MetadataExpressionItem(
                        Range.Create(_single_test_file, 33, 5, 38, 40),
                        IdentifierExpression(Range.Create(_single_test_file, 33, 5, 33, 35), "multiline_triple_string_single"),
                        StringExpression(Range.Create(_single_test_file, 33, 37, 38, 40), "And more\n    testing\n  for\ndifferent types."),
                    ),
                ],
            ),
        ),
    ]


# ----------------------------------------------------------------------
class TestMultilineStringErrors(object):
    # ----------------------------------------------------------------------
    def test_InvalidPrefix(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("Triple-quote delimiters that initiate multiline strings must not have any trailing content. (single_test_file [2, 15])"),
        ):
            _Test(
                textwrap.dedent(
                    '''\
                    data: String {
                        value: """Invalid Prefix
                               Content should start here.
                               """
                    }
                    ''',
                ),
                quiet=True,
            )

    # ----------------------------------------------------------------------
    def test_InvalidSuffix(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("Triple-quote delimiters that terminate multiline strings must not have any preceding content. (single_test_file [4, 12])"),
        ):
            _Test(
                textwrap.dedent(
                    '''\
                    data: String {
                        value: """
                               Content should start and end here.
                               InvalidSuffix"""
                    }
                    ''',
                ),
                quiet=True,
            )

    # ----------------------------------------------------------------------
    def test_InvalidLinePrefix(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("Invalid multiline string indentation. (single_test_file [4, 10])"),
        ):
            _Test(
                textwrap.dedent(
                    '''\
                    data: String {
                        value: """
                               Line 1
                             Line2
                               Line 3
                               """
                    }
                    ''',
                ),
                quiet=True,
            )


# ----------------------------------------------------------------------
def test_TupleType():
    assert _Test(
        textwrap.dedent(
            """\
            data1: One,
            data2: One, Two_,
            """,
        ),
    )[0] == [
        DataMemberStatement(
            Range.Create(_single_test_file, 1, 1, 2, 1),
            IdentifierExpression(Range.Create(_single_test_file, 1, 1, 1, 6), "data1"),
            TupleType(
                Range.Create(_single_test_file, 1, 8, 1, 12),
                [
                    IdentifierType(Range.Create(_single_test_file, 1, 8, 1, 11), "One"),
                ],
            ),
            None,
        ),
        DataMemberStatement(
            Range.Create(_single_test_file, 2, 1, 3, 1),
            IdentifierExpression(Range.Create(_single_test_file, 2, 1, 2, 6), "data2"),
            TupleType(
                Range.Create(_single_test_file, 2, 8, 2, 18),
                [
                    IdentifierType(Range.Create(_single_test_file, 2, 8, 2, 11), "One"),
                    IdentifierType(Range.Create(_single_test_file, 2, 13, 2, 17), "Two_"),
                ],
            ),
            None,
        ),
    ]


# ----------------------------------------------------------------------
def test_VariantType():
    assert _Test(
        textwrap.dedent(
            """\
            data1: One | Two
            data2: One | Two | Three
            """,
        ),
    )[0] == [
        DataMemberStatement(
            Range.Create(_single_test_file, 1, 1, 2, 1),
            IdentifierExpression(Range.Create(_single_test_file, 1, 1, 1, 6), "data1"),
            VariantType(
                Range.Create(_single_test_file, 1, 8, 1, 17),
                [
                    IdentifierType(Range.Create(_single_test_file, 1, 8, 1, 11), "One"),
                    IdentifierType(Range.Create(_single_test_file, 1, 14, 1, 17), "Two"),
                ],
            ),
            None,
        ),
        DataMemberStatement(
            Range.Create(_single_test_file, 2, 1, 3, 1),
            IdentifierExpression(Range.Create(_single_test_file, 2, 1, 2, 6), "data2"),
            VariantType(
                Range.Create(_single_test_file, 2, 8, 2, 25),
                [
                    IdentifierType(Range.Create(_single_test_file, 2, 8, 2, 11), "One"),
                    IdentifierType(Range.Create(_single_test_file, 2, 14, 2, 17), "Two"),
                    IdentifierType(Range.Create(_single_test_file, 2, 20, 2, 25), "Three"),
                ],
            ),
            None,
        ),
    ]


# ----------------------------------------------------------------------
class TestExtensions(object):
    # ----------------------------------------------------------------------
    def test_Empty(self):
        assert _Test(
            textwrap.dedent(
                """\
                extension_func()
                """,
            ),
        )[0] == [
            ExtensionStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1,1, 15), "extension_func"),
                [],
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_SinglePositionalSingleLine(self):
        assert _Test(
            textwrap.dedent(
                """\
                func1(one)
                func2(arg_one,)
                """,
            ),
        )[0] == [
            ExtensionStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 6), "func1"),
                [
                    Identifier(Range.Create(_single_test_file, 1, 7, 1, 10), "one"),
                ],
                [],
            ),
            ExtensionStatement(
                Range.Create(_single_test_file, 2, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 2, 1, 2, 6), "func2"),
                [
                    Identifier(Range.Create(_single_test_file, 2, 7, 2, 14), "arg_one"),
                ],
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_MultiplePositionalSingleLine(self):
        assert _Test(
            textwrap.dedent(
                """\
                first_func(one, 1, "three")
                second_func(one_arg, 20, "three", )
                """,
            ),
        )[0] == [
            ExtensionStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 11), "first_func"),
                [
                    Identifier(Range.Create(_single_test_file, 1, 12, 1, 15), "one"),
                    IntegerExpression(Range.Create(_single_test_file, 1, 17, 1, 18), 1),
                    StringExpression(Range.Create(_single_test_file, 1, 20, 1, 27), "three"),
                ],
                [],
            ),
            ExtensionStatement(
                Range.Create(_single_test_file, 2, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 2, 1, 2, 12), "second_func"),
                [
                    Identifier(Range.Create(_single_test_file, 2, 13, 2, 20), "one_arg"),
                    IntegerExpression(Range.Create(_single_test_file, 2, 22, 2, 24), 20),
                    StringExpression(Range.Create(_single_test_file, 2, 26, 2, 33), "three"),
                ],
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_SingleKeywordSingleLine(self):
        assert _Test(
            textwrap.dedent(
                """\
                Func1(key=foo)
                FuncTwo(Key="foo",)
                """,
            ),
        )[0] == [
            ExtensionStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 6), "Func1"),
                [],
                [
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 1, 7, 1, 14),
                        Identifier(Range.Create(_single_test_file, 1, 7, 1, 10), "key"),
                        Identifier(Range.Create(_single_test_file, 1, 11, 1, 14), "foo"),
                    ),
                ],
            ),
            ExtensionStatement(
                Range.Create(_single_test_file, 2, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 2, 1, 2, 8), "FuncTwo"),
                [],
                [
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 2, 9, 2, 18),
                        Identifier(Range.Create(_single_test_file, 2, 9, 2, 12), "Key"),
                        StringExpression(Range.Create(_single_test_file, 2, 13, 2, 18), "foo"),
                    ),
                ],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_MultipleKeywordSingleLine(self):
        assert _Test(
            textwrap.dedent(
                """\
                Func1(one = "two", three=4, five  =6.0)
                """,
            ),
        )[0] == [
            ExtensionStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 6), "Func1"),
                [],
                [
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 1, 7, 1, 18),
                        Identifier(Range.Create(_single_test_file, 1, 7, 1, 10), "one"),
                        StringExpression(Range.Create(_single_test_file, 1, 13, 1, 18), "two"),
                    ),
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 1, 20, 1, 27),
                        Identifier(Range.Create(_single_test_file, 1, 20, 1, 25), "three"),
                        IntegerExpression(Range.Create(_single_test_file, 1, 26, 1, 27), 4),
                    ),
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 1, 29, 1, 39),
                        Identifier(Range.Create(_single_test_file, 1, 29, 1, 33), "five"),
                        NumberExpression(Range.Create(_single_test_file, 1, 36, 1, 39), 6.0),
                    ),
                ],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_PositionalAndKeywordSingleLine(self):
        assert _Test(
            textwrap.dedent(
                """\
                func(1, "two", 3.0, four=five, six=Seven)
                """,
            ),
        )[0] == [
            ExtensionStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 5), "func"),
                [
                    IntegerExpression(Range.Create(_single_test_file, 1, 6, 1, 7), 1),
                    StringExpression(Range.Create(_single_test_file, 1, 9, 1, 14), "two"),
                    NumberExpression(Range.Create(_single_test_file, 1, 16, 1, 19), 3.0),
                ],
                [
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 1, 21, 1, 30),
                        Identifier(Range.Create(_single_test_file, 1, 21, 1, 25), "four"),
                        Identifier(Range.Create(_single_test_file, 1, 26, 1, 30), "five"),
                    ),
                    ExtensionStatementKeywordArg(
                        Range.Create(_single_test_file, 1, 32, 1, 41),
                        Identifier(Range.Create(_single_test_file, 1, 32, 1, 35), "six"),
                        Identifier(Range.Create(_single_test_file, 1, 36, 1, 41), "Seven"),
                    ),
                ],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_Multiline(self):
        # ----------------------------------------------------------------------
        SimpleMappingType                   = Union[
            str,                            # Identifier / StringExpression (surrounding quotes are added to string)
            int,                            # IntegerExpression
            float,                          # NumberExpression
            bool,                           # BooleanExpression
        ]

        # ----------------------------------------------------------------------
        def ToSimpleMappingType(
            element: Element,
        ) -> SimpleMappingType:  # type: ignore
            if isinstance(element, Identifier):
                return element.value
            elif isinstance(element, StringExpression):
                return '"{}"'.format(element.value)
            elif isinstance(element, IntegerExpression):
                return element.value
            elif isinstance(element, NumberExpression):
                return element.value
            elif isinstance(element, BooleanExpression):
                return element.value
            else:
                assert False, element  # pragma: no cover

        # ----------------------------------------------------------------------
        def SimpleExtension(
            statement: ExtensionStatement,
        ) -> Tuple[str, List[SimpleMappingType], Dict[str, SimpleMappingType]]:  # type: ignore
            return (
                statement.name.value,
                [ToSimpleMappingType(element) for element in statement.positional_args],
                {
                    key: ToSimpleMappingType(value.value)
                    for key, value in statement.keyword_args.items()
                },
            )

        # ----------------------------------------------------------------------

        results = _Test(
            textwrap.dedent(
                """\
                Func1(
                    one, two,
                    three,
                )

                func2(one, two
                    three=3.14,
                    four="four",
                )
                """,
            ),
        )[0]

        assert all(isinstance(result, ExtensionStatement) for result in results)

        assert SimpleExtension(cast(ExtensionStatement, results[0])) == (
            "Func1",
            ["one", "two", "three"],
            {},
        )

        assert SimpleExtension(cast(ExtensionStatement, results[1])) == (
            "func2",
            ["one", "two"],
            {
                "three": 3.14,
                "four": '"four"',
            },
        )


# ----------------------------------------------------------------------
class TestCompoundStatements(object):
    # ----------------------------------------------------------------------
    def test_SimpleSingleLinePass(self):
        assert _Test(
            textwrap.dedent(
                """\
                Foo -> pass
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 4), "Foo"),
                None,
                None,
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_SimpleMulitlinePass(self):
        assert _Test(
            textwrap.dedent(
                """\
                EmptyType ->
                    pass
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 10), "EmptyType"),
                None,
                None,
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_Bases(self):
        assert _Test(
            textwrap.dedent(
                """\
                TypeWithBase: Foo -> pass
                TypeWithTupleBase: One, Two, -> pass
                TypeWithVariantBase: One | Two | Three -> pass
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 2, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 13), "TypeWithBase"),
                IdentifierType(Range.Create(_single_test_file, 1, 15, 1, 18), "Foo"),
                None,
                [],
            ),
            CompoundStatement(
                Range.Create(_single_test_file, 2, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 2, 1, 2, 18), "TypeWithTupleBase"),
                TupleType(
                    Range.Create(_single_test_file, 2, 20, 2, 29),
                    [
                        IdentifierType(Range.Create(_single_test_file, 2, 20, 2, 23), "One"),
                        IdentifierType(Range.Create(_single_test_file, 2, 25, 2, 28), "Two"),
                    ],
                ),
                None,
                [],
            ),
            CompoundStatement(
                Range.Create(_single_test_file, 3, 1, 4, 1),
                Identifier(Range.Create(_single_test_file, 3, 1, 3, 20), "TypeWithVariantBase"),
                VariantType(
                    Range.Create(_single_test_file, 3, 22, 3, 39),
                    [
                        IdentifierType(Range.Create(_single_test_file, 3, 22, 3, 25), "One"),
                        IdentifierType(Range.Create(_single_test_file, 3, 28, 3, 31), "Two"),
                        IdentifierType(Range.Create(_single_test_file, 3, 34, 3, 39), "Three"),
                    ],
                ),
                None,
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_Metadata(self):
        assert _Test(
            textwrap.dedent(
                """\
                Type1 {one: two, a: "b" } -> pass

                Type2 {
                    one: Two
                } -> pass

                Type3: Base1, Base2, {
                    five: 6.0
                    seven: true
                    eight: 800000
                } ->
                    pass
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 6), "Type1"),
                None,
                MetadataExpression(
                    Range.Create(_single_test_file, 1, 7, 1, 26),
                    [
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 1, 8, 1, 16),
                            IdentifierExpression(Range.Create(_single_test_file, 1, 8, 1, 11), "one"),
                            Identifier(Range.Create(_single_test_file, 1, 13, 1, 16), "two"),
                        ),
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 1, 18, 1, 24),
                            IdentifierExpression(Range.Create(_single_test_file, 1, 18, 1, 19), "a"),
                            StringExpression(Range.Create(_single_test_file, 1, 21, 1, 24), "b"),
                        ),
                    ],
                ),
                [],
            ),
            CompoundStatement(
                Range.Create(_single_test_file, 3, 1, 7, 1),
                Identifier(Range.Create(_single_test_file, 3, 1, 3, 6), "Type2"),
                None,
                MetadataExpression(
                    Range.Create(_single_test_file, 3, 7, 5, 2),
                    [
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 4, 5, 4, 13),
                            IdentifierExpression(Range.Create(_single_test_file, 4, 5, 4, 8), "one"),
                            Identifier(Range.Create(_single_test_file, 4, 10, 4, 13), "Two"),
                        ),
                    ],
                ),
                [],
            ),
            CompoundStatement(
                Range.Create(_single_test_file, 7, 1, 13, 1),
                Identifier(Range.Create(_single_test_file, 7, 1, 7, 6), "Type3"),
                TupleType(
                    Range.Create(_single_test_file, 7, 8, 7, 21),
                    [
                        IdentifierType(Range.Create(_single_test_file, 7, 8, 7, 13), "Base1"),
                        IdentifierType(Range.Create(_single_test_file, 7, 15, 7, 20), "Base2"),
                    ],
                ),
                MetadataExpression(
                    Range.Create(_single_test_file, 7, 22, 11, 2),
                    [
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 8, 5, 8, 14),
                            IdentifierExpression(Range.Create(_single_test_file, 8, 5, 8, 9), "five"),
                            NumberExpression(Range.Create(_single_test_file, 8, 11, 8, 14), 6.0),
                        ),
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 9, 5, 9, 16),
                            IdentifierExpression(Range.Create(_single_test_file, 9, 5, 9, 10), "seven"),
                            BooleanExpression(Range.Create(_single_test_file, 9, 12, 9, 16), True),
                        ),
                        MetadataExpressionItem(
                            Range.Create(_single_test_file, 10, 5, 10, 18),
                            IdentifierExpression(Range.Create(_single_test_file, 10, 5, 10, 10), "eight"),
                            IntegerExpression(Range.Create(_single_test_file, 10, 12, 10, 18), 800000),
                        ),
                    ],
                ),
                [],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_SingleStatement(self):
        assert _Test(
            textwrap.dedent(
                """\
                Type1 ->
                    one: Two

                Type2 ->
                    one: Two {metadata: 1}

                Type3 ->
                    one: Two {
                        metadata1: 4
                        metadata2: "five"
                    }
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 3, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 6), "Type1"),
                None,
                None,
                [
                    DataMemberStatement(
                        Range.Create(_single_test_file, 2, 5, 3, 1),
                        IdentifierExpression(Range.Create(_single_test_file, 2, 5, 2, 8), "one"),
                        IdentifierType(Range.Create(_single_test_file, 2, 10, 2, 13), "Two"),
                        None,
                    ),
                ],
            ),
            CompoundStatement(
                Range.Create(_single_test_file, 4, 1, 6, 1),
                Identifier(Range.Create(_single_test_file, 4, 1, 4, 6), "Type2"),
                None,
                None,
                [
                    DataMemberStatement(
                        Range.Create(_single_test_file, 5, 5, 6, 1),
                        IdentifierExpression(Range.Create(_single_test_file, 5, 5, 5, 8), "one"),
                        IdentifierType(Range.Create(_single_test_file, 5, 10, 5, 13), "Two"),
                        MetadataExpression(
                            Range.Create(_single_test_file, 5, 14, 5, 27),
                            [
                                MetadataExpressionItem(
                                    Range.Create(_single_test_file, 5, 15, 5, 26),
                                    IdentifierExpression(Range.Create(_single_test_file, 5, 15, 5, 23), "metadata"),
                                    IntegerExpression(Range.Create(_single_test_file, 5, 25, 5, 26), 1),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
            CompoundStatement(
                Range.Create(_single_test_file, 7, 1, 12, 1),
                Identifier(Range.Create(_single_test_file, 7, 1, 7, 6), "Type3"),
                None,
                None,
                [
                    DataMemberStatement(
                        Range.Create(_single_test_file, 8, 5, 12, 1),
                        IdentifierExpression(Range.Create(_single_test_file, 8, 5, 8, 8), "one"),
                        IdentifierType(Range.Create(_single_test_file, 8, 10, 8, 13), "Two"),
                        MetadataExpression(
                            Range.Create(_single_test_file, 8, 14, 11, 6),
                            [
                                MetadataExpressionItem(
                                    Range.Create(_single_test_file, 9, 9, 9, 21),
                                    IdentifierExpression(Range.Create(_single_test_file, 9, 9, 9, 18), "metadata1"),
                                    IntegerExpression(Range.Create(_single_test_file, 9, 20, 9, 21), 4),
                                ),
                                MetadataExpressionItem(
                                    Range.Create(_single_test_file, 10, 9, 10, 26),
                                    IdentifierExpression(Range.Create(_single_test_file, 10, 9, 10, 18), "metadata2"),
                                    StringExpression(Range.Create(_single_test_file, 10, 20, 10, 26), "five"),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_MultipleStatements(self):
        assert _Test(
            textwrap.dedent(
                """\
                Type ->
                    one: Two
                    three: Four
                    five: Six {
                        metadata: 1
                    }

                    seven: Eight

                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 10, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 5), "Type"),
                None,
                None,
                [
                    DataMemberStatement(
                        Range.Create(_single_test_file, 2, 5, 3, 5),
                        IdentifierExpression(Range.Create(_single_test_file, 2, 5, 2, 8), "one"),
                        IdentifierType(Range.Create(_single_test_file, 2, 10, 2, 13), "Two"),
                        None,
                    ),
                    DataMemberStatement(
                        Range.Create(_single_test_file, 3, 5, 4, 5),
                        IdentifierExpression(Range.Create(_single_test_file, 3, 5, 3, 10), "three"),
                        IdentifierType(Range.Create(_single_test_file, 3, 12, 3, 16), "Four"),
                        None,
                    ),
                    DataMemberStatement(
                        Range.Create(_single_test_file, 4, 5, 8, 5),
                        IdentifierExpression(Range.Create(_single_test_file, 4, 5, 4, 9), "five"),
                        IdentifierType(Range.Create(_single_test_file, 4, 11, 4, 14), "Six"),
                        MetadataExpression(
                            Range.Create(_single_test_file, 4, 15, 6, 6),
                            [
                                MetadataExpressionItem(
                                    Range.Create(_single_test_file, 5, 9, 5, 20),
                                    IdentifierExpression(Range.Create(_single_test_file, 5, 9, 5, 17), "metadata"),
                                    IntegerExpression(Range.Create(_single_test_file, 5, 19, 5, 20), 1),
                                ),
                            ],
                        ),
                    ),
                    DataMemberStatement(
                        Range.Create(_single_test_file, 8, 5, 10, 1),
                        IdentifierExpression(Range.Create(_single_test_file, 8, 5, 8, 10), "seven"),
                        IdentifierType(Range.Create(_single_test_file, 8, 12, 8, 17), "Eight"),
                        None,
                    ),
                ],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_NestedType(self):
        assert _Test(
            textwrap.dedent(
                """\
                Type ->
                    NestedType ->
                        one: Two
                    three: Four
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 5, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 5), "Type"),
                None,
                None,
                [
                    CompoundStatement(
                        Range.Create(_single_test_file, 2, 5, 3, 17),
                        Identifier(Range.Create(_single_test_file, 2, 5, 2, 15), "NestedType"),
                        None,
                        None,
                        [
                            DataMemberStatement(
                                Range.Create(_single_test_file, 3, 9, 3, 17),
                                IdentifierExpression(Range.Create(_single_test_file, 3, 9, 3, 12), "one"),
                                IdentifierType(Range.Create(_single_test_file, 3, 14, 3, 17), "Two"),
                                None,
                            ),
                        ],
                    ),
                    DataMemberStatement(
                        Range.Create(_single_test_file, 4, 5, 5, 1),
                        IdentifierExpression(Range.Create(_single_test_file, 4, 5, 4, 10), "three"),
                        IdentifierType(Range.Create(_single_test_file, 4, 12, 4, 16), "Four"),
                        None,
                    ),
                ],
            ),
        ]

    # ----------------------------------------------------------------------
    def test_TypeHierarchy(self):
        assert _Test(
            textwrap.dedent(
                """\
                Type1 ->
                    one: Two

                    Child ->
                        Grandchild ->
                            three: Four

                        five: Six
                """,
            ),
        )[0] == [
            CompoundStatement(
                Range.Create(_single_test_file, 1, 1, 9, 1),
                Identifier(Range.Create(_single_test_file, 1, 1, 1, 6), "Type1"),
                None,
                None,
                [
                    DataMemberStatement(
                        Range.Create(_single_test_file, 2, 5, 4, 5),
                        IdentifierExpression(Range.Create(_single_test_file, 2, 5, 2, 8), "one"),
                        IdentifierType(Range.Create(_single_test_file, 2, 10, 2, 13), "Two"),
                        None,
                    ),
                    CompoundStatement(
                        Range.Create(_single_test_file, 4, 5, 9, 1),
                        Identifier(Range.Create(_single_test_file, 4, 5, 4, 10), "Child"),
                        None,
                        None,
                        [
                            CompoundStatement(
                                Range.Create(_single_test_file, 5, 9, 7, 1),
                                Identifier(Range.Create(_single_test_file, 5, 9, 5, 19), "Grandchild"),
                                None,
                                None,
                                [
                                    DataMemberStatement(
                                        Range.Create(_single_test_file, 6, 13, 7, 1),
                                        IdentifierExpression(Range.Create(_single_test_file, 6, 13, 6, 18), "three"),
                                        IdentifierType(Range.Create(_single_test_file, 6, 20, 6, 24), "Four"),
                                        None,
                                    ),
                                ],
                            ),
                            DataMemberStatement(
                                Range.Create(_single_test_file, 8, 9, 9, 1),
                                IdentifierExpression(Range.Create(_single_test_file, 8, 9, 8, 13), "five"),
                                IdentifierType(Range.Create(_single_test_file, 8, 15, 8, 18), "Six"),
                                None,
                            ),
                        ],
                    ),
                ],
            ),
        ]


# ----------------------------------------------------------------------
class TestInclude(object):
    # ----------------------------------------------------------------------
    def test_Valid(self):
        test_file = Path("test_file")
        included_file = Path("included_file.SimpleSchema")

        # ----------------------------------------------------------------------
        def NewIsFile(
            filename: Path,
        ) -> bool:
            return filename.name == included_file.name

        # ----------------------------------------------------------------------
        def NewOpen(*args, **kwargs):
            the_mock = mock.MagicMock()

            the_mock.__enter__().read.return_value = textwrap.dedent(
                """\
                three: Four
                five: Six
                """,
            )

            return the_mock

        # ----------------------------------------------------------------------

        with (
            mock.patch.object(Path, "is_file", NewIsFile),
            mock.patch.object(Path, "open", NewOpen),
        ):
            results, output = _TestEx(
                textwrap.dedent(
                    """\
                    simple_schema_include "included_file.SimpleSchema"

                    one: Two
                    """,
                ),
            )

        assert len(results) == 2
        assert test_file in results
        assert included_file in results

        assert cast(RootStatement, results[test_file]).statements == [
            DataMemberStatement(
                Range.Create(test_file, 3, 1, 4, 1),
                IdentifierExpression(Range.Create(test_file, 3, 1, 3, 4), "one"),
                IdentifierType(Range.Create(test_file, 3, 6, 3, 9), "Two"),
                None,
            ),
        ]

        assert cast(RootStatement, results[included_file]).statements == [
            DataMemberStatement(
                Range.Create(included_file, 1, 1, 2, 1),
                IdentifierExpression(Range.Create(included_file, 1, 1, 1, 6), "three"),
                IdentifierType(Range.Create(included_file, 1, 8, 1, 12), "Four"),
                None,
            ),
            DataMemberStatement(
                Range.Create(included_file, 2, 1, 3, 1),
                IdentifierExpression(Range.Create(included_file, 2, 1, 2, 5), "five"),
                IdentifierType(Range.Create(included_file, 2, 7, 2, 10), "Six"),
                None,
            ),
        ]

    # ----------------------------------------------------------------------
    def test_InvalidFile(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The included file 'InvalidFile' is not valid. (test_file <[1, 23] -> [1, 36]>)"),
        ):
            _TestEx(
                textwrap.dedent(
                    """\
                    simple_schema_include "InvalidFile"
                    """,
                ),
                quiet=True,
            )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _TestEx(
    content: str,
    filename: Path=Path("test_file"),
    *,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[Dict[Path, Union[Exception, RootStatement]], str]:
    dm_and_sink = iter(GenerateDoneManagerAndSink())

    results = Parse(
        cast(DoneManager, next(dm_and_sink)),
        [(filename, lambda: content)],
        single_threaded=False,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert results is not None

    output = cast(str, next(dm_and_sink))

    return results, output


# ----------------------------------------------------------------------
_single_test_file                           = Path("single_test_file")

def _Test(
    content: str,
    *,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[List[Statement], str]:
    results, output = _TestEx(
        content,
        _single_test_file,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert len(results) == 1
    assert _single_test_file in results

    result = results[_single_test_file]

    if isinstance(result, Exception):
        return [], output

    return result.statements, output
