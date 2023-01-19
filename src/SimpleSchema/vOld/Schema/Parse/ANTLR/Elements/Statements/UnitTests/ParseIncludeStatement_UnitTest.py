# ----------------------------------------------------------------------
# |
# |  ParseIncludeStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-21 10:13:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
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
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Element import SimpleElement
    from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, Visibility
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementItem, ParseIncludeStatementType


# ----------------------------------------------------------------------
class TestIncludeStatementItem(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        # With element name and reference name
        id_range = mock.MagicMock()

        element_name_id = Identifier(
            mock.MagicMock(),
            SimpleElement(id_range, "The element name"),
            SimpleElement(mock.MagicMock(), Visibility.Public),
        )

        reference_name_id = mock.MagicMock()

        item_range = mock.MagicMock()

        item = ParseIncludeStatementItem(item_range, element_name_id, reference_name_id)

        assert item.range is item_range
        assert item.element_name is element_name_id
        assert item.reference_name is reference_name_id

        # With element name
        item = ParseIncludeStatementItem(item_range, element_name_id, None)

        assert item.range is item_range
        assert item.element_name is element_name_id

        assert item.reference_name.range is id_range
        assert item.reference_name.id is element_name_id.id
        assert item.reference_name.visibility.value == Visibility.Private
        assert item.reference_name.visibility.range is item_range

    # ----------------------------------------------------------------------
    def test_ErrorNotType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Imported elements must be types. (bad file <[1, 2] -> [3, 4]>)"),
        ):
            ParseIncludeStatementItem(
                mock.MagicMock(),
                Identifier(
                    Range.Create(Path("bad file"), 1, 2, 3, 4),
                    SimpleElement(mock.MagicMock(), "invalid name"),
                    SimpleElement(mock.MagicMock(), Visibility.Public),
                ),
                None,
            )

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize("visibility", [Visibility.Protected, Visibility.Private])
    def test_ErrorNotVisible(self, visibility):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'ValidName' is not a public type. (another bad file <[10, 20] -> [30, 40]>)"),
        ):
            ParseIncludeStatementItem(
                mock.MagicMock(),
                Identifier(
                    Range.Create(Path("another bad file"), 10, 20, 30, 40),
                    SimpleElement(mock.MagicMock(), "ValidName"),
                    SimpleElement(mock.MagicMock(), visibility),
                ),
                None,
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidReference(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Reference elements must be types. (bad file <[2, 4] -> [6, 8]>)"),
        ):
            ParseIncludeStatementItem(
                mock.MagicMock(),
                Identifier(
                    mock.MagicMock(),
                    SimpleElement(mock.MagicMock(), "ValidName"),
                    SimpleElement(mock.MagicMock(), Visibility.Public),
                ),
                Identifier(
                    Range.Create(Path("bad file"), 2, 4, 6, 8),
                    SimpleElement(mock.MagicMock(), "invalid reference name"),
                    SimpleElement(mock.MagicMock(), mock.MagicMock()),
                ),
            )


# ----------------------------------------------------------------------
class TestIncludeStatement(object):
    # ----------------------------------------------------------------------
    def test_Construct(self):
        range = mock.MagicMock()
        the_type = ParseIncludeStatementType.Star
        this_file = SimpleElement(mock.MagicMock(), Path(__file__))

        statement = ParseIncludeStatement(range, the_type, this_file, [])

        assert statement.range is range
        assert statement.include_type is the_type
        assert statement.filename is this_file
        assert statement.items == []

        the_type = ParseIncludeStatementType.Named
        items = [mock.MagicMock(), mock.MagicMock()]

        statement = ParseIncludeStatement(range, the_type, this_file, items)  # type: ignore

        assert statement.range is range
        assert statement.include_type is the_type
        assert statement.filename is this_file
        assert statement.items is items

    # ----------------------------------------------------------------------
    def test_ErrorInvalidFile(self):
        filename = Path(str(uuid.uuid4()))

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'{}' is not a valid file. (bad file <[11, 21] -> [31, 41]>)".format(filename)),
        ):
            ParseIncludeStatement(
                mock.MagicMock(),
                ParseIncludeStatementType.Star,
                SimpleElement(Range.Create(Path("bad file"), 11, 21, 31, 41), filename),
                [],
            )

    # ----------------------------------------------------------------------
    def test_ErrorItemsExpected(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("Items were expected. (file <[1, 2] -> [3, 4]>)"),
        ):
            ParseIncludeStatement(
                Range.Create(Path("file"), 1, 2, 3, 4),
                ParseIncludeStatementType.Named,
                SimpleElement(mock.MagicMock(), Path(__file__)),
                [],
            )

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize("include_type", [ParseIncludeStatementType.Module, ParseIncludeStatementType.Star])
    def test_ErrorItemsNotExpected(self, include_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("No items were expected. (file <[1, 2] -> [3, 4]>)"),
        ):
            ParseIncludeStatement(
                Range.Create(Path("file"), 1, 2, 3, 4),
                include_type,
                SimpleElement(mock.MagicMock(), Path(__file__)),
                [mock.MagicMock(), mock.MagicMock()],
            )
