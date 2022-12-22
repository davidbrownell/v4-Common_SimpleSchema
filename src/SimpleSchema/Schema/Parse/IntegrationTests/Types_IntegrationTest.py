# ----------------------------------------------------------------------
# |
# |  Types_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 11:19:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration tests for types"""

import sys
import textwrap

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Parse.IntegrationTests.Impl.TestHelpers import CompareResultsFromFile, Test


# ----------------------------------------------------------------------
def test_ElementReference():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                value1: Type::element
                value2: One.Two::element
                value3: One.Two.Three::element+
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Tuple():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                name1: (One, )
                name2: (One::element, )
                name3: (One, Two)
                name4: (One, Two, )
                name5: (One, Two, Three)
                name6: (One?, Two { m1: True })* { m2: 2.0 }
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Variant():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                name1: (One | Two)
                name2: (One* | Two+)
                name3: (One | Two {m1: 1})+ {
                    m2: "two"
                }

                name4: (
                    One
                    | Two
                    | Three
                ) {
                    m1: 1
                    m2: "two"
                }
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Visibility():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                public_name: Value1
                @protected_name: Value2
                _private_name: Value3
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Dotted():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                name1: One.Two.Three
                name2: One.Two.Three?
                name3: One.Two.Three { m1: True }
                """,
            ),
        )[0],
    )
