# ----------------------------------------------------------------------
# |
# |  Expression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 10:52:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Expression.py"""

import re
import sys

from pathlib import Path
from typing import ClassVar
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
def test_Standard():
    # ----------------------------------------------------------------------
    class MyExpression(Expression):
        NAME: ClassVar[str] = "MyExpression"

    # ----------------------------------------------------------------------

    range_value = Mock()

    e = MyExpression(range_value, "this_value")

    assert e.range is range_value
    assert e.NAME == "MyExpression"
    assert e.value == "this_value"


# ----------------------------------------------------------------------
def test_Error():
    with pytest.raises(
        AssertionError,
        match=re.escape("Make sure to define the expression's name."),
    ):
        Expression(Mock(), 1234)
