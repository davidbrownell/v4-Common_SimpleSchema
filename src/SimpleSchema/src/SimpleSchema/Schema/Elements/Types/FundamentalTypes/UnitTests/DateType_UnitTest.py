# ----------------------------------------------------------------------
# |
# |  DateType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 15:00:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for DateType.py"""

import re
import sys

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DateType import DateType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()

    dt = DateType(range_mock)

    assert dt.NAME == "Date"
    assert dt.SUPPORTED_PYTHON_TYPES == (date, )

    assert dt.range is range_mock


# ----------------------------------------------------------------------
def test_DisplayType():
    assert DateType(Mock()).display_type == "Date"


# ----------------------------------------------------------------------
def test_ToPython():
    value = date.today()

    assert DateType(Mock()).ToPython(value) == value
