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
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Identifier import SimpleElement, Visibility
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Elements.Expressions.IdentifierExpression import IdentifierExpression


# ----------------------------------------------------------------------
def test_Standard():
    r1 = Range.Create(Path("i_file"), 2, 4, 6, 8)
    r2 = Range.Create(Path("r2"), 1, 2, 3, 4)
    r3 = Range.Create(Path("r3"), 10, 20, 30, 40)

    i = IdentifierExpression(
        r1,
        SimpleElement(r2, "the_value"),
        SimpleElement(r3, Visibility.Protected),
    )

    assert i.range is r1
    assert i.id.value == "the_value"
    assert i.id.range is r2
    assert i.visibility.value == Visibility.Protected
    assert i.visibility.range is r3


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
            IdentifierExpression(
                Range.Create(Path("file_for_invalid_content"), 1, 2, 3, 4),
                SimpleElement(mock.MagicMock(), invalid_value),
                SimpleElement(mock.MagicMock(), mock.MagicMock()),
            )
