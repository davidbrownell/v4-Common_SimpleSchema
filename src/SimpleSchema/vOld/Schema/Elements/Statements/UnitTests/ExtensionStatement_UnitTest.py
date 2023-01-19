# ----------------------------------------------------------------------
# |
# |  ExtensionStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:13:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ExtensionStatement.py"""

import re
import sys

from pathlib import Path
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
    from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, Visibility
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg


# ----------------------------------------------------------------------
def test_ExtensionStatementKeywordArg():
    range1 = Range.Create(Path("keyword arg file"), 11, 22, 33, 44)
    range2 = Range.Create(Path("element_file"), 1, 2, 3, 4)

    arg = ExtensionStatementKeywordArg(
        range1,
        Identifier(mock.MagicMock(), SimpleElement(mock.MagicMock(), "id_value"), SimpleElement(mock.MagicMock(), Visibility.Public)),
        Element(range2),
    )

    assert arg.range is range1
    assert arg.name.id.value == "id_value"
    assert arg.name.visibility.value == Visibility.Public
    assert arg.value.range is range2


# ----------------------------------------------------------------------
class TestExtensionStatement(object):
    # ----------------------------------------------------------------------
    def test_Empty(self):
        e = ExtensionStatement(
            Range.Create(Path("extension"), 1, 2, 3, 4),
            Identifier(
                mock.MagicMock(),
                SimpleElement(mock.MagicMock(), "id"),
                SimpleElement(mock.MagicMock(), Visibility.Private),
            ),
            [],
            [],
        )

        assert e.range == Range.Create(Path("extension"), 1, 2, 3, 4)
        assert e.name.id.value == "id"
        assert e.name.visibility.value == Visibility.Private
        assert e.positional_args == []
        assert e.keyword_args == {}

    # ----------------------------------------------------------------------
    def test_PositionalAndKeywordArgs(self):
        p1 = Element(Range.Create(Path("p1"), 10, 20, 30, 40))
        p2 = Element(Range.Create(Path("p2"), 11, 21, 31, 41))

        keyword_args = {
            "foo": ExtensionStatementKeywordArg(
                mock.MagicMock(),
                Identifier(
                    mock.MagicMock(),
                    SimpleElement(mock.MagicMock(), "foo"),
                    SimpleElement(mock.MagicMock(), Visibility.Protected),
                ),
                Element(mock.MagicMock()),
            ),
            "bar": ExtensionStatementKeywordArg(
                mock.MagicMock(),
                Identifier(
                    mock.MagicMock(),
                    SimpleElement(mock.MagicMock(), "bar"),
                    SimpleElement(mock.MagicMock(), mock.MagicMock()),
                ),
                Element(mock.MagicMock()),
            ),
            "baz": ExtensionStatementKeywordArg(
                mock.MagicMock(),
                Identifier(
                    mock.MagicMock(),
                    SimpleElement(mock.MagicMock(), "baz"),
                    SimpleElement(mock.MagicMock(), mock.MagicMock()),
                ),
                Element(mock.MagicMock()),
            ),
        }

        range1 = Range.Create(Path("extension"), 1, 2, 3, 4)

        e = ExtensionStatement(
            range1,
            Identifier(
                mock.MagicMock(),
                SimpleElement(mock.MagicMock(), "extension_name"),
                SimpleElement(mock.MagicMock(), Visibility.Private),
            ),
            [p1, p2],
            list(keyword_args.values()),
        )

        assert e.range is range1
        assert e.name.id.value == "extension_name"
        assert e.name.visibility.value == Visibility.Private

        assert e.positional_args == [p1, p2]
        assert e.keyword_args == keyword_args

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateKeyword(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("An argument for the parameter 'id' has already been provided at <[10, 20] -> [30, 40]>. (bar_id <[11, 22] -> [33, 44]>)"),
        ):
            ExtensionStatement(
                mock.MagicMock(),
                Identifier(
                    mock.MagicMock(),
                    SimpleElement(mock.MagicMock(), "extension_name"),
                    SimpleElement(mock.MagicMock(), mock.MagicMock()),
                ),
                [],
                [
                    ExtensionStatementKeywordArg(
                        mock.MagicMock(),
                        Identifier(
                            Range.Create(Path("foo_id"), 10, 20, 30, 40),
                            SimpleElement(mock.MagicMock(), "id"),
                            SimpleElement(mock.MagicMock(), mock.MagicMock()),
                        ),
                        Element(mock.MagicMock()),
                    ),
                    ExtensionStatementKeywordArg(
                        mock.MagicMock(),
                        Identifier(
                            Range.Create(Path("bar_id"), 11, 22, 33, 44),
                            SimpleElement(mock.MagicMock(), "id"),
                            SimpleElement(mock.MagicMock(), mock.MagicMock()),
                        ),
                        Element(mock.MagicMock()),
                    ),
                ],
            )
