# ----------------------------------------------------------------------
# |
# |  ParseType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-28 18:03:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for ParseType.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Parse.ParseElements.Types.ParseType import ParseType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = mock.MagicMock()
    cardinality_mock = mock.MagicMock()
    metadata_mock = mock.MagicMock()

    t = ParseType(range_mock, cardinality_mock, None)

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is None

    t = ParseType(range_mock, cardinality_mock, metadata_mock)

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is metadata_mock