# ----------------------------------------------------------------------
# |
# |  StructureStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 11:54:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration tests for structure statements"""

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
def test_SingleLine():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                foo -> pass
                Foo -> pass

                Optional? -> pass
                WithMetadata { value: 1 } -> pass

                CardinalityAndMetadata[3, 11] { value: 1 } -> pass
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_NoStatementsMultiLine():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Foo ->
                    pass

                Optional? ->
                    pass

                WithMetadata1 { value1: 1, value2: 2 } ->
                    pass

                WithMetadata2 {
                    value1: 1
                    value2: 2
                } ->
                    pass

                CardinalityAndMetadata[3, 11] {
                    value1: 1
                } ->
                    pass
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_WithBase():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Simple1: String -> pass
                Simple2: String ->
                    pass

                Optional: String? ->
                    pass

                WithMetadata1: String { value: 1 } ->
                    pass

                WithMetadata2: String+ {
                    value1: 1
                    value2: 2
                } ->
                    pass
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Items():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                One: (A | B | C) ->
                    value1: String
                    value2: Boolean
                    value3: Filename { exists: False }
                """,
            ),
        )[0],
    )


# ----------------------------------------------------------------------
def test_Nested():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Child ->
                    Parent ->
                        Grandparent ->
                            name: String

                        grandparent: Grandparent

                    value1: String
                    value2: Boolean
                """,
            ),
        )[0],
    )
