# ----------------------------------------------------------------------
# |
# |  ItemStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-17 15:48:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration tests for Item Statements"""

import re
import sys
import textwrap

from pathlib import Path

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Parse import AntlrException
    from SimpleSchema.Schema.Parse.IntegrationTests.Impl.TestHelpers import CompareResultsFromFile, Test, DEFAULT_WORKSPACE_PATH


# ----------------------------------------------------------------------
def test_Simple():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                foo: Bar
                Foo: Bar
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Cardinality():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                name0: Value
                name1: Value?
                name2: Value*
                name3: Value+
                name4: Value[3]
                name5: Value[3,10]
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Metadata():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                name0: Value0 { pass }
                name1: Value1 { one: 2 }
                name2: Value2 { one: 2, three: 4.0 }
                name3: Value3 {
                  pass
                }

                name4: Value4 {
                  one: 2
                }

                name5: Value5 {
                  one: 2
                  three: 4.0
                }

                name6: Value6? { one: 2 }
                name7: Value7* { one: 2 }
                name8: Value8+ { one: 2 }
                name9: Value9[3] { one: 2 }
                name10: Value10[3, 10] { one: 2 }
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_MetadataTypes():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                # This item isn't meaningful, it is only a vessel for metadata
                name: Value {{
                  # Identifier values
                  identifier: "identifier_value"

                  # Number values
                  positive_number: 12345.6789
                  negative_number: -123.123
                  no_prefix_positive_number: .6789
                  no_prefix_negative_number: -.123

                  # Integer values
                  positive_integer: 123
                  negative_integer: -10

                  # Strings
                  basic_string: "This is a basic string."
                  basic_string_escapes: "This is an \\"escaped\\" string."

                  single_quote_string: 'This is a single-quote string.'
                  single_quote_string_escapes: 'This is an \\'escaped\\' single-quote string.'

                  multi_line_string1: {triple_quote}
                                      This is
                                        an
                                          example
                                      of a
                                          multiline
                                      string!
                                      {triple_quote}

                  multi_line_string2: '''
                                      A multiline string
                                      with
                                        different
                                      quote
                                      types!
                                      '''

                  true_value1: y
                  true_value2: Y
                  true_value3: yes
                  true_value4: Yes
                  true_value5: YES
                  true_value6: true
                  true_value7: True
                  true_value8: TRUE
                  true_value9: on
                  true_value10: On
                  true_value11: ON

                  false_value1: n
                  false_value2: N
                  false_value3: no
                  false_value4: No
                  false_value5: NO
                  false_value6: false
                  false_value7: False
                  false_value8: FALSE
                  false_value9: off
                  false_value10: Off
                  false_value11: OFF

                  list1: []
                  list2: [ "one"]
                  list3: [ "one", ]
                  list4: [
                    "one"
                  ]
                  list5: [
                    "one",
                  ]
                  list6: ["one", 2.0, 3, True]
                  list7: ["one", 2.0, 3, True, ]
                  list8: [
                    "one",
                    2.0,
                    3
                  ]
                  list9: [
                    "one",
                    2.0,
                    3,
                  ]
                }}
                """,
            ).format(triple_quote='"""'),
        )[0],
    )


# ----------------------------------------------------------------------
class TestMultilineStringErrors(object):
    # ----------------------------------------------------------------------
    def test_InvalidOpeningToken(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("Triple-quote delimiters that initiate multiline strings cannot have any content on the same line. ({} [2, 27])".format(DEFAULT_WORKSPACE_PATH / "root_file")),
        ):
            Test(
                textwrap.dedent(
                    """\
                    name: Value {
                        invalid_multiline: '''No content should be here
                                           More content.
                                           '''
                    }
                    """,
                ),
                quiet=True,
            )

    # ----------------------------------------------------------------------
    def test_InvalidClosingToken(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("Triple-quote delimiters that terminate multiline strings cannot have any content on the same line. ({} [4, 24])".format(DEFAULT_WORKSPACE_PATH / "root_file")),
        ):
            Test(
                textwrap.dedent(
                    """\
                    name: Value {
                        invalid_multiline: '''
                                           Some content.
                                           No content should be here'''
                    }
                    """,
                ),
                quiet=True,
            )

    # ----------------------------------------------------------------------
    def test_InvalidIndentation(self):
        with pytest.raises(
            AntlrException,
            match=re.escape("Invalid multiline string indentation. ({} [4, 20])".format(DEFAULT_WORKSPACE_PATH / "root_file")),
        ):
            Test(
                textwrap.dedent(
                    """\
                    name: Value {
                        invalid_multiline: '''
                                           This line is valid.
                                       This line has indentation that is not aligned.
                                           '''
                    }
                    """,
                ),
                quiet=True,
            )
