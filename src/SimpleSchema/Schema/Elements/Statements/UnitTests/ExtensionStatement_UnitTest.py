# ----------------------------------------------------------------------
# |
# |  ExtensionStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 10:06:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ExtensionStatement.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg, SimpleElement


# ----------------------------------------------------------------------
class TestExtensionStatementKeywordArg(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        range_mock = Mock()
        name_mock = Mock()
        expression_mock = Mock()

        eska = ExtensionStatementKeywordArg(range_mock, name_mock, expression_mock)

        assert eska.range is range_mock
        assert eska.name is name_mock
        assert eska.expression is expression_mock


# ----------------------------------------------------------------------
class TestExtensionStatement(object):
    # ----------------------------------------------------------------------
    def test_NoArgs(self):
        range_mock = Mock()
        name_mock = Mock()

        e = ExtensionStatement(range_mock, name_mock, [], [])

        assert e.range is range_mock
        assert e.name is name_mock
        assert e.positional_args == []
        assert e.keyword_args == {}

    # ----------------------------------------------------------------------
    def test_PositionalArgs(self):
        range_mock = Mock()
        name_mock = Mock()
        positional_mock = Mock()

        e = ExtensionStatement(range_mock, name_mock, positional_mock, [])

        assert e.range is range_mock
        assert e.name is name_mock
        assert e.positional_args is positional_mock
        assert e.keyword_args == {}

    # ----------------------------------------------------------------------
    def test_KeywordArgs(self):
        range_mock = Mock()
        name_mock = Mock()

        keyword_args: dict[str, ExtensionStatementKeywordArg] = {
            "arg1": ExtensionStatementKeywordArg(Mock(), SimpleElement[str](Mock(), "arg1"), Mock()),
            "arg2": ExtensionStatementKeywordArg(Mock(), SimpleElement[str](Mock(), "arg2"), Mock()),
        }

        e = ExtensionStatement(range_mock, name_mock, [], list(keyword_args.values()))

        assert e.range is range_mock
        assert e.name is name_mock
        assert e.positional_args == []
        assert e.keyword_args == keyword_args

    # ----------------------------------------------------------------------
    def test_ErrorDuplicateKeywordArgs(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("An argument for the parameter 'arg' was already provided at 'filename <Ln 1, Col 2 -> Ln 3, Col 4>'. (filename <Ln 10, Col 20 -> Ln 30, Col 40>)"),
        ):
            ExtensionStatement(
                Mock(),
                Mock(),
                [],
                [
                    ExtensionStatementKeywordArg(
                        Mock(),
                        SimpleElement[str](Range.Create(Path("filename"), 1, 2, 3, 4), "arg"),
                        Mock(),
                    ),
                    ExtensionStatementKeywordArg(
                        Mock(),
                        SimpleElement[str](Mock(), "unique_arg"),
                        Mock(),
                    ),
                    ExtensionStatementKeywordArg(
                        Mock(),
                        SimpleElement[str](Range.Create(Path("filename"), 10, 20, 30, 40), "arg"),
                        Mock(),
                    ),

                ],
            )
