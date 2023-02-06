# ----------------------------------------------------------------------
# |
# |  DateTimeType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 14:57:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for DateTimeType.py"""

import re
import sys

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DateTimeType import DateTimeType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    dtt = DateTimeType(range_mock, cardinality_mock, metadata_mock)

    assert dtt.NAME == "DateTime"
    assert dtt.SUPPORTED_PYTHON_TYPES == (datetime, )

    assert dtt.range is range_mock
    assert dtt.cardinality is cardinality_mock
    assert dtt.metadata is metadata_mock


# ----------------------------------------------------------------------
def test_DisplayName():
    assert DateTimeType(Mock(), Cardinality.CreateFromCode(), None).display_name == "DateTime"


# ----------------------------------------------------------------------
def test_ToPython():
    value = datetime.now()

    assert DateTimeType(Mock(), Cardinality.CreateFromCode(), None).ToPython(value) == value
