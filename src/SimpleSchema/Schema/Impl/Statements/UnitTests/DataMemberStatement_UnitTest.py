# ----------------------------------------------------------------------
# |
# |  DataMemberStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:13:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for DataMemberStatement.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Statements.DataMemberStatement import DataMemberStatement, IdentifierExpression, Type, MetadataExpression


# ----------------------------------------------------------------------
def test_NoMetadata():
    data = DataMemberStatement(
        Range.Create(Path("the file"), 1, 2, 3, 4),
        IdentifierExpression(Range.Create(Path("the id"), 1, 2, 3, 4), "id"),
        Type(Range.Create(Path("type"), 1, 2, 3, 4)),
        None,
    )

    assert data.range == Range.Create(Path("the file"), 1, 2, 3, 4)
    assert data.name.value == "id"
    assert data.the_type.range == Range.Create(Path("type"), 1, 2, 3, 4)
    assert data.metadata is None


# ----------------------------------------------------------------------
def test_WithMetadata():
    metadata_mock = mock.MagicMock()

    data = DataMemberStatement(
        Range.Create(Path("the file"), 1, 2, 3, 4),
        IdentifierExpression(Range.Create(Path("the id"), 1, 2, 3, 4), "id"),
        Type(Range.Create(Path("type"), 1, 2, 3, 4)),
        metadata_mock,
    )

    assert data.range == Range.Create(Path("the file"), 1, 2, 3, 4)
    assert data.name.value == "id"
    assert data.the_type.range == Range.Create(Path("type"), 1, 2, 3, 4)
    assert data.metadata is metadata_mock
