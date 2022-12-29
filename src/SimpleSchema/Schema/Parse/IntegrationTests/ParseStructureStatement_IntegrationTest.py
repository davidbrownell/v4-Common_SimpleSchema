# ----------------------------------------------------------------------
# |
# |  ParseStructureStatement_IntegrationTest.py
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
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Parse.IntegrationTests.Impl.TestHelpers import CompareResultsFromFile, Test, DEFAULT_WORKSPACE_PATH


# ----------------------------------------------------------------------
def test_NoStatements():
    CompareResultsFromFile(
        Test(
            textwrap.dedent(
                """\
                Foo ->
                    pass

                Optional ->
                    pass
                ?

                WithMetadata1 ->
                    pass
                { value1: 1, value2: 2 }

                WithMetadata2 ->
                    pass
                {
                    value1: 1
                    value2: 2
                }

                CardinalityAndMetadata  ->
                    pass
                {
                    value1: 1
                } [3, 11]
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
                Simple: String ->
                    pass

                Optional: String ->
                    pass
                ?

                WithMetadata1: String { value: 1 } ->
                    pass

                WithMetadata2: String {
                    value1: 1
                    value2: 2
                } ->
                    pass
                +
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


# ----------------------------------------------------------------------
def test_ErrorInvalidCardinality():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            "Structure bases cannot have cardinality values. ({} <[1, 15] -> [1, 16]>)".format(
                DEFAULT_WORKSPACE_PATH / "root_file",
            ),
        ),
    ):
        Test(
            textwrap.dedent(
                """\
                Struct: String+ ->
                    pass
                """,
            ),
            quiet=True,
        )
