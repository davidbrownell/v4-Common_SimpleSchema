# ----------------------------------------------------------------------
# |
# |  GuidType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 14:44:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for GuidType.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock
from uuid import UUID, uuid4

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.GuidType import GuidType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    gt = GuidType(range_mock, cardinality_mock, metadata_mock)

    assert gt.NAME == "Guid"
    assert gt.SUPPORTED_PYTHON_TYPES == (UUID, )

    assert gt.range is range_mock
    assert gt.cardinality is cardinality_mock
    assert gt.metadata is metadata_mock


# ----------------------------------------------------------------------
def test_DisplayName():
    assert GuidType(Mock(), Cardinality.CreateFromCode(0, 1), None).display_name == "Guid?"
    assert GuidType(Mock(), Cardinality.CreateFromCode(0, None), None).display_name == "Guid*"


# ----------------------------------------------------------------------
def test_Clone():
    gt = GuidType(Mock(), Mock(), Mock())

    assert gt.Clone() == gt


# ----------------------------------------------------------------------
def test_ToPython():
    value = uuid4()

    assert GuidType(Mock(), Cardinality.CreateFromCode(), None).ToPython(value) == value