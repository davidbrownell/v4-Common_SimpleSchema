# ----------------------------------------------------------------------
# |
# |  TimeType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 13:58:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TimeType.py"""

import sys

from datetime import datetime, time
from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.TimeType import TimeType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()

    tt = TimeType(range_mock)

    assert tt.NAME == "Time"
    assert tt.SUPPORTED_PYTHON_TYPES == (time, )

    assert tt.range is range_mock


# ----------------------------------------------------------------------
def test_DisplayType():
    assert TimeType(Mock()).display_type == "Time"


# ----------------------------------------------------------------------
def test_ToPython():
    value = datetime.now().time()

    assert TimeType(Mock()).ToPython(value) == value
