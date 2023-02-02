# ----------------------------------------------------------------------
# |
# |  FundamentalType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 15:31:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for FundamentalType.py"""

import sys

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Tuple, Type as PythonType
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyFundamentalType(FundamentalType):
    NAME: ClassVar[str]                                                     = "MyFundamentalType"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        return MyFundamentalType(*args, **kwargs)


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    ft = MyFundamentalType(range_mock, cardinality_mock, metadata_mock)

    assert ft.range is range_mock
    assert ft.cardinality is cardinality_mock
    assert ft.metadata is metadata_mock

    assert ft.ToPython(10) == 10
