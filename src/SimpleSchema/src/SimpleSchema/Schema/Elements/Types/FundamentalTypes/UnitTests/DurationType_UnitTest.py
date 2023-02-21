# ----------------------------------------------------------------------
# |
# |  DurationType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 14:51:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for DurationType.py"""

import re
import sys

from datetime import timedelta
from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DurationType import DurationType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()

    dt = DurationType(range_mock)

    assert dt.NAME == "Duration"
    assert dt.SUPPORTED_PYTHON_TYPES == (timedelta, )

    assert dt.range is range_mock


# ----------------------------------------------------------------------
def test_DisplayType():
    assert DurationType(Mock()).display_type == "Duration"


# ----------------------------------------------------------------------
def test_ToPython():
    value = timedelta(seconds=1.234)

    assert DurationType(Mock()).ToPython(value) == value
