# ----------------------------------------------------------------------
# |
# |  IdentifierExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 10:36:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for IdentifierExpression.py"""

import re
import sys

from pathlib import Path

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Impl.Expressions.IdentifierExpression import IdentifierExpression


# ----------------------------------------------------------------------
def test_Standard():
    i = IdentifierExpression(Range.Create(Path("i_file"), 2, 4, 6, 8), "the_value")

    assert i.range == Range.Create(Path("i_file"), 2, 4, 6, 8)
    assert i.value == "the_value"


# ----------------------------------------------------------------------
def test_Invalid():
    for invalid_value in [
        "InvalidValue",
        "_InvalidValue",
    ]:
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'{}' is not a valid expression; identifier expressions must begin with a lowercase letter. (file_for_invalid_content <[1, 2] -> [3, 4]>)".format(invalid_value)),
        ):
            IdentifierExpression(Range.Create(Path("file_for_invalid_content"), 1, 2, 3, 4), invalid_value)
