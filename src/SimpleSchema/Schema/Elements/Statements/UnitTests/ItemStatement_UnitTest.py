# ----------------------------------------------------------------------
# |
# |  ItemStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 12:43:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ItemStatement.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Common.Identifier import SimpleElement
    from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement, Identifier, Type


# ----------------------------------------------------------------------
def test_Standard():
    range1 = mock.MagicMock()
    range2 = mock.MagicMock()
    range3 = mock.MagicMock()
    range4 = mock.MagicMock()

    data = ItemStatement(
        range1,
        Identifier(
            range2,
            SimpleElement(mock.MagicMock(), "id"),
            SimpleElement(mock.MagicMock(), mock.MagicMock()),
        ),
        Type(
            range3,
            Cardinality(range4, None, None),
            None,
        ),
    )

    assert data.range is range1

    assert data.name.range is range2
    assert data.name.id.value == "id"

    assert data.type.range is range3
    assert data.type.cardinality.range is range4
    assert data.type.cardinality.is_single is True
    assert data.type.metadata is None
