# ----------------------------------------------------------------------
# |
# |  Metadata_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 12:02:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Metadata.py"""

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
    from SimpleSchema.Schema.Impl.Common.Identifier import Visibility, SimpleElement
    from SimpleSchema.Schema.Impl.Common.Metadata import Metadata, MetadataItem
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Impl.Expressions.IdentifierExpression import IdentifierExpression


# ----------------------------------------------------------------------
def test_MetadataItem():
    path = Path("mei")

    mei = MetadataItem(
        Range.Create(path, 1, 2, 3, 4),
        IdentifierExpression(Range.Create(path, 1, 2, 1, 10), SimpleElement(mock.MagicMock(), "foo"), Visibility.Public),
        IdentifierExpression(Range.Create(path, 1, 10, 1, 20), SimpleElement(mock.MagicMock(), "bar"), Visibility.Public),
    )

    assert mei.range == Range.Create(path, 1, 2, 3, 4)
    assert mei.name.id.value == "foo"
    assert mei.value.id.value == "bar"  # type: ignore


# ----------------------------------------------------------------------
def test_Metadata():
    path = Path("me")

    mei1 = MetadataItem(
        Range.Create(path, 1, 1, 1, 40),
        IdentifierExpression(Range.Create(path, 1, 1, 1, 10), SimpleElement(mock.MagicMock(), "foo"), Visibility.Public),
        IdentifierExpression(Range.Create(path, 1, 10, 1, 20), SimpleElement(mock.MagicMock(), "bar"), Visibility.Public),
    )

    mei2 = MetadataItem(
        Range.Create(path, 2, 1, 2, 40),
        IdentifierExpression(Range.Create(path, 2, 1, 2, 10), SimpleElement(mock.MagicMock(), "biz"), Visibility.Public),
        IdentifierExpression(Range.Create(path, 2, 10, 2, 20), SimpleElement(mock.MagicMock(), "baz"), Visibility.Public),
    )

    me = Metadata(Range.Create(path, 1, 1, 3, 1), [mei1, mei2])

    assert me.range == Range.Create(path, 1, 1, 3, 1)
    assert me.items == {
        "foo": mei1,
        "biz": mei2,
    }


# ----------------------------------------------------------------------
def test_DuplicateNames():
    path = Path("me")

    mei1 = MetadataItem(
        Range.Create(path, 1, 1, 1, 40),
        IdentifierExpression(Range.Create(path, 1, 1, 1, 10), SimpleElement(mock.MagicMock(), "same_name"), Visibility.Public),
        IdentifierExpression(Range.Create(path, 1, 10, 1, 20), SimpleElement(mock.MagicMock(), "bar"), Visibility.Public),
    )

    mei2 = MetadataItem(
        Range.Create(path, 2, 1, 2, 40),
        IdentifierExpression(Range.Create(path, 2, 1, 2, 10), SimpleElement(mock.MagicMock(), "same_name"), Visibility.Public),
        IdentifierExpression(Range.Create(path, 2, 10, 2, 20), SimpleElement(mock.MagicMock(), "baz"), Visibility.Public),
    )

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("The metadata item 'same_name' has already been provided at <[1, 1] -> [1, 10]>. (me <[2, 1] -> [2, 10]>)"),
    ):
        Metadata(Range.Create(path, 1, 1, 3, 1), [mei1, mei2])
