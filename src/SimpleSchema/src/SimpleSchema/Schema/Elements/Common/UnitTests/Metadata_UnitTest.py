# ----------------------------------------------------------------------
# |
# |  Metadata_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 09:59:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Metadata.py"""

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

    from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement


# ----------------------------------------------------------------------
def test_MetadataItem():
    range_mock = Mock()
    name_mock = Mock()
    expression_mock = Mock()

    mi = MetadataItem(range_mock, name_mock, expression_mock)

    assert mi.range is range_mock
    assert mi.name is name_mock
    assert mi.expression is expression_mock


# ----------------------------------------------------------------------
def test_MetadataEmpty():
    range_mock = Mock()

    m = Metadata(range_mock, [])

    assert m.range is range_mock
    assert m.CHILDREN_NAME == "items"
    assert m.items == {}


# ----------------------------------------------------------------------
def test_MetadataMultipleItems():
    range_mock = Mock()

    mi1 = MetadataItem(Mock(), SimpleElement[str](Mock(), "item1"), Mock())
    mi2 = MetadataItem(Mock(), SimpleElement[str](Mock(), "item2"), Mock())

    m = Metadata(range_mock, [mi1, mi2])

    assert m.range is range_mock
    assert m.CHILDREN_NAME == "items"

    assert m.items == {
        "item1": mi1,
        "item2": mi2,
    }


# ----------------------------------------------------------------------
def test_ErrorDuplicateItems():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("The metadata item 'item' has already been provided at file <Ln 1, Col 2 -> Ln 3, Col 4>. (file <Ln 10, Col 20 -> Ln 30, Col 40>)"),
    ):
        Metadata(
            Mock(),
            [
                MetadataItem(
                    Mock(),
                    SimpleElement[str](Range.Create(Path("file"), 1, 2, 3, 4), "item"),
                    Mock(),
                ),
                MetadataItem(
                    Mock(),
                    SimpleElement[str](Range.Create(Path("file"), 10, 20, 30, 40), "item"),
                    Mock(),
                ),
            ],
        )
