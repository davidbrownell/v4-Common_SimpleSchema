# ----------------------------------------------------------------------
# |
# |  ParseIncludeStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 08:59:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseIncludeStatement.py"""

import re
import sys
import uuid

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseIncludeStatement import ParseIdentifier, ParseIncludeStatement, ParseIncludeStatementItem, ParseIncludeStatementType, SimpleElement


# ----------------------------------------------------------------------
class TestParseIncludeStatementItem(object):
    # ----------------------------------------------------------------------
    def test_DefaultRef(self):
        range_mock = Mock()
        name = ParseIdentifier(Mock(), "ImportedType")
        reference_name = ParseIdentifier(Mock(), "ReferenceType")

        pisi = ParseIncludeStatementItem(range_mock, name, reference_name)

        assert pisi.range is range_mock
        assert pisi.element_name is name
        assert pisi.reference_name is reference_name

    # ----------------------------------------------------------------------
    def test_ErrorNotAType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("The imported element 'not_a_type' is not a type. (the file <Ln 2, Col 4 -> Ln 6, Col 8>)"),
        ):
            ParseIncludeStatementItem(
                Mock(),
                ParseIdentifier(Range.Create(Path("the file"), 2, 4, 6, 8), "not_a_type"),
                Mock(),
            )

    # ----------------------------------------------------------------------
    def test_ErrorNotATypeReference(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'not_a_type' is not a type name. (the file <Ln 2, Col 4 -> Ln 6, Col 8>)"),
        ):
            ParseIncludeStatementItem(
                Mock(),
                ParseIdentifier(Mock(), "ValidType"),
                ParseIdentifier(Range.Create(Path("the file"), 2, 4, 6, 8), "not_a_type"),
            )


# ----------------------------------------------------------------------
class TestParseIncludeStatement(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        range_mock = Mock()
        filename_mock = Mock()
        items_mock = []

        pis = ParseIncludeStatement(range_mock, ParseIncludeStatementType.Module, filename_mock, items_mock)

        assert pis.range is range_mock
        assert pis.include_type == ParseIncludeStatementType.Module
        assert pis.filename is filename_mock
        assert pis.items is items_mock

    # ----------------------------------------------------------------------
    def test_ErrorInvalidFile(self):
        filename = str(uuid.uuid4())

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'{}' is not a valid file. (a b c <Ln 2, Col 4 -> Ln 6, Col 8>)".format(filename)),
        ):
            ParseIncludeStatement(
                Mock(),
                ParseIncludeStatementType.Module,
                SimpleElement(Range.Create(Path("a b c"), 2, 4, 6, 8), Path(filename)),
                [],
            )

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize("type_value", [ParseIncludeStatementType.Module, ParseIncludeStatementType.Star])
    def test_ErrorInvalidItems(self, type_value):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("No items were expected. (1, 2, 3 <Ln 2, Col 4 -> Ln 6, Col 8>)"),
        ):
            ParseIncludeStatement(
                Range.Create(Path("1, 2, 3"), 2, 4, 6, 8),
                type_value,
                SimpleElement(Mock(), Path(__file__)),
                [Mock(), ],
            )

    # ----------------------------------------------------------------------
    def test_ErrorMissingItems(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Items were expected. (a-b-c <Ln 2, Col 4 -> Ln 6, Col 8>)"),
        ):
            ParseIncludeStatement(
                Range.Create(Path("a-b-c"), 2, 4, 6, 8),
                ParseIncludeStatementType.Named,
                SimpleElement(Mock(), Path(__file__)),
                [],
            )
