# ----------------------------------------------------------------------
# |
# |  TupleExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-30 08:59:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TupleExpression.py"""

import re
import sys

from pathlib import Path
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression, Expression


# ----------------------------------------------------------------------
def test_Standard():
    the_range = mock.MagicMock()
    expressions = [mock.MagicMock(), ]

    e = TupleExpression(the_range, expressions)  # type: ignore

    assert e.range is the_range
    assert e.expressions is expressions


# ----------------------------------------------------------------------
def test_Error():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No expressions were provided. (a file <[1, 3] -> [5, 7]>)"),
    ):
        TupleExpression(
            Range.Create(Path("a file"), 1, 3, 5, 7),
            [],
        )
