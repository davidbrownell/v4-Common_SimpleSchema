# ----------------------------------------------------------------------
# |
# |  TupleExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 12:46:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TupleExpression.py"""

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

    from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    expressions_mock = [Mock(), ]

    t = TupleExpression(range_mock, expressions_mock)  # type: ignore

    assert t.range is range_mock
    assert t.NAME == "Tuple"
    assert t.value is expressions_mock


# ----------------------------------------------------------------------
def test_ErrorEmpty():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No expressions were provided. (FILENAME <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        TupleExpression(
            Range.Create(Path("FILENAME"), 1, 2, 3, 4),
            [],
        )
