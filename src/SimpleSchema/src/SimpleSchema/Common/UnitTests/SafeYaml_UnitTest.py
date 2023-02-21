# ----------------------------------------------------------------------
# |
# |  SafeYaml_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-08 13:44:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for SafeYaml.py"""

import random
import re
import string
import sys
import textwrap

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.SafeYaml import ToYamlString


# NOTE: These tests cannot be run in parallel with each other, as they modify the global imports.


# ----------------------------------------------------------------------
def test_ErrorImport():
    # This test must be run before the other tests, as the other tests will
    # create the monkey patched dumper in SafeYaml.

    with pytest.raises(
        Exception,
        match=re.escape("This function must be called before rtyaml is imported."),
    ):
        import rtyaml

        # ----------------------------------------------------------------------
        def OnExit():
            del sys.modules["rtyaml"]

        # ----------------------------------------------------------------------

        with ExitStack(OnExit):
            ToYamlString({})


# ----------------------------------------------------------------------
def test_Standard():
    # ----------------------------------------------------------------------
    def GenerateRandomString(
        num_chars: int,
    ) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=num_chars))

    # ----------------------------------------------------------------------

    long_key = GenerateRandomString(200)
    long_value = GenerateRandomString(500)

    d = {
        long_key: "value",
        "long_value": long_value,
        "_{}".format(long_key): long_value,
    }

    assert ToYamlString(d) == textwrap.dedent(
        """\
        {long_key}: value
        long_value: {long_value}
        _{long_key}: {long_value}
        """,
    ).format(
        long_key=long_key,
        long_value=long_value,
    )
