# ----------------------------------------------------------------------
# |
# |  UniqueNameTrait_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-22 15:19:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for UniqueNameTrait.py"""


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
    from SimpleSchema.Schema.Elements.Common.UniqueNameTrait import UniqueNameTrait


# ----------------------------------------------------------------------
def test_Standard():
    r = UniqueNameTrait()

    assert r.is_unique_name_normalized is False

    with pytest.raises(AssertionError):
        r.unique_name

    r.NormalizeUniqueName("unique_name")
    assert r.unique_name == "unique_name"

    with pytest.raises(AssertionError):
        r.NormalizeUniqueName("different_name")
