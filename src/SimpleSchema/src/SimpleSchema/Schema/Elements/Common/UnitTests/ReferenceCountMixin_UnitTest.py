# ----------------------------------------------------------------------
# |
# |  ReferenceCountMixin_UnitTest.py
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
"""Unit tests for ReferenceCountMixin.py"""


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
    from SimpleSchema.Schema.Elements.Common.ReferenceCountMixin import ReferenceCountMixin


# ----------------------------------------------------------------------
def test_Standard():
    r = ReferenceCountMixin()

    assert r.reference_count == 0

    r.Increment()
    assert r.reference_count == 1

    r.Increment()
    assert r.reference_count == 2


# ----------------------------------------------------------------------
def test_Finalize():
    r = ReferenceCountMixin()

    assert r.is_unique_type_name_finalized is False

    with pytest.raises(AssertionError):
        r.unique_type_name

    r.FinalizeUniqueTypeName("unique_name")
    assert r.unique_type_name == "unique_name"

    with pytest.raises(AssertionError):
        r.FinalizeUniqueTypeName("different_name")
