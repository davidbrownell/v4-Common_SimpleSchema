# ----------------------------------------------------------------------
# |
# |  ParseType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:13:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseType.py"""

import re
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Tuple, Type as PythonType
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseType import ParseType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyParseType(ParseType):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "MyParseType"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    mpt = MyParseType(range_mock, cardinality_mock, metadata_mock)

    assert mpt.range is range_mock
    assert mpt.cardinality is cardinality_mock
    assert mpt.metadata is metadata_mock


# ----------------------------------------------------------------------
def test_ErrorValidatePythonItem():
    with pytest.raises(
        Exception,
        match=re.escape("This method should never be called on ParseType instances."),
    ):
        MyParseType(Mock(), Cardinality.CreateFromCode(), None).ToPython("foo")
