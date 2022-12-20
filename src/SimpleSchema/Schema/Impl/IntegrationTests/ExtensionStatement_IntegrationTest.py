# ----------------------------------------------------------------------
# |
# |  ExtensionStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 11:53:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration tests for extension statements"""

import sys
import textwrap

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.IntegrationTests.Impl.TestHelpers import CompareResultsFromFile, Test


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Foo()
                foo()

                Func(

                )
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_PositionalArg():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Func1(one)
                Func2(one, )
                Func3(
                    one
                )
                Func4(
                    # Comment Before
                    one,
                    # Comment after

                )
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_PositionalArgs():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Func1(1, 2)
                Func2(1, 2, )
                Func3(
                    1,
                        2,
                  3,
                )
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_KeywordArg():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Func1(a=1)
                Func2(a=1, )
                Func3(
                    a=
                        1

                        ,
                )
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_KeywordArgs():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Func1(a=1, b=2)
                Func2(a=1, b=2, c=3, )

                Func3(
                    a=1,
                    b=2,
                    c=three,
                )
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_PositionalAndKeywordArgs():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Func1(1, 2, 3, a=1.0, )

                Func2(
                    10,
                    20,
                    "thirty",
                    a=1.0,
                    b=2.0,
                    c=3.0,
                )
                """,
            ),
        )[0],
    )
