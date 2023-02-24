# ----------------------------------------------------------------------
# |
# |  JsonSchemaPlugin_EndToEndTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-21 08:15:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""End-to-end tests for JsonSchemaPlugin"""

from pathlib import Path

from Common_Foundation import PathEx

from .TestHelpers import Test

# code_coverage: include = ../JsonSchemaPlugin.py
# code_coverage: include = ../../SimpleSchema/Plugin.py


# ----------------------------------------------------------------------
def test_Standard(tmp_path):
    Test(
        "JsonSchema",
        tmp_path,
        PathEx.EnsureDir(Path(__file__).parent / "Results" / "JsonSchemaPlugin"),
        "--filter-unsupported-extensions",
        "--filter-unsupported-metadata",
    )
