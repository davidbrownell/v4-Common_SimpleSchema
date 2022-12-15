# ----------------------------------------------------------------------
# |
# |  IdentifierType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:15:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for IdentifierType.py"""

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
    from SimpleSchema.Schema.Impl.Types.IdentifierType import IdentifierType


# ----------------------------------------------------------------------
def test_Standard():
    i = IdentifierType(Range.Create(Path("identifier_file"), 1, 2, 3, 4), "TheType")

    assert i.range == Range.Create(Path("identifier_file"), 1, 2, 3, 4)
    assert i.value == "TheType"


# ----------------------------------------------------------------------
def test_Invalid():
    for invalid_value in [
        "invalidValue",
        "_invalidValue",
    ]:
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'{}' is not a valid type; identifier types must begin with an uppercase letter. (file_for_invalid_content <[1, 2] -> [3, 4]>)".format(invalid_value)),
        ):
            IdentifierType(Range.Create(Path("file_for_invalid_content"), 1, 2, 3, 4), invalid_value)
