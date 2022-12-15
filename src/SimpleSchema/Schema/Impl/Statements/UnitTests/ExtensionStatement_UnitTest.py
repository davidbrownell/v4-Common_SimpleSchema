# ----------------------------------------------------------------------
# |
# |  ExtensionStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:13:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ExtensionStatement.py"""

import re
import sys

from pathlib import Path

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Element import Element
    from SimpleSchema.Schema.Impl.Common.Identifier import Identifier
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Impl.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg


# ----------------------------------------------------------------------
def test_ExtensionStatementKeywordArg():
    arg = ExtensionStatementKeywordArg(
        Range.Create(Path("keyword arg file"), 11, 22, 33, 44),
        Identifier(Range.Create(Path("id"), 1, 2, 3, 4), "id_value"),
        Element(Range.Create(Path("element"), 2, 4, 6, 8)),
    )

    assert arg.range == Range.Create(Path("keyword arg file"), 11, 22, 33, 44)
    assert arg.name.value == "id_value"
    assert arg.value.range.filename == Path("element")


# ----------------------------------------------------------------------
class TestExtensionStatement(object):
    # ----------------------------------------------------------------------
    def test_Empty(self):
        e = ExtensionStatement(
            Range.Create(Path("extension"), 1, 2, 3, 4),
            Identifier(Range.Create(Path("id"), 11, 22, 33, 44), "id"),
            [],
            [],
        )

        assert e.range == Range.Create(Path("extension"), 1, 2, 3, 4)
        assert e.name.value == "id"
        assert e.positional_args == []
        assert e.keyword_args == {}

    # ----------------------------------------------------------------------
    def test_PositionalAndKeywordArgs(self):
        p1 = Element(Range.Create(Path("p1"), 10, 20, 30, 40))
        p2 = Element(Range.Create(Path("p2"), 11, 21, 31, 41))

        keyword_args = {
            "foo": ExtensionStatementKeywordArg(
                Range.Create(Path("foo"), 1, 2, 3, 4),
                Identifier(Range.Create(Path("foo_id"), 1, 2, 3, 4), "foo"),
                Element(Range.Create(Path("foo_value"), 1, 2, 3, 4)),
            ),
            "bar": ExtensionStatementKeywordArg(
                Range.Create(Path("bar"), 1, 2, 3, 4),
                Identifier(Range.Create(Path("bar_id"), 1, 2, 3, 4), "bar"),
                Element(Range.Create(Path("bar_value"), 1, 2, 3, 4)),
            ),
            "baz": ExtensionStatementKeywordArg(
                Range.Create(Path("baz"), 1, 2, 3, 4),
                Identifier(Range.Create(Path("baz_id"), 1, 2, 3, 4), "baz"),
                Element(Range.Create(Path("baz_value"), 1, 2, 3, 4)),
            ),
        }

        e = ExtensionStatement(
            Range.Create(Path("extension"), 1, 2, 3, 4),
            Identifier(Range.Create(Path("extension"), 1, 2, 3, 4), "extension_name"),
            [p1, p2],
            list(keyword_args.values()),
        )

        assert e.range == Range.Create(Path("extension"), 1, 2, 3, 4)
        assert e.name.value == "extension_name"
        assert e.positional_args == [p1, p2]
        assert e.keyword_args == keyword_args

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateKeyword(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("An argument for the parameter 'id' has already been provided at <[10, 20] -> [30, 40]>. (bar_id <[11, 22] -> [33, 44]>)"),
        ):
            ExtensionStatement(
                Range.Create(Path("extension"), 1, 2, 3, 4),
                Identifier(Range.Create(Path("extension"), 1, 2, 3, 4), "extension_name"),
                [],
                [
                    ExtensionStatementKeywordArg(
                        Range.Create(Path("foo"), 1, 2, 3, 4),
                        Identifier(Range.Create(Path("foo_id"), 10, 20, 30, 40), "id"),
                        Element(Range.Create(Path("foo_value"), 1, 2, 3, 4)),
                    ),
                    ExtensionStatementKeywordArg(
                        Range.Create(Path("bar"), 1, 2, 3, 4),
                        Identifier(Range.Create(Path("bar_id"), 11, 22, 33, 44), "id"),
                        Element(Range.Create(Path("bar_value"), 1, 2, 3, 4)),
                    ),
                ],
            )
