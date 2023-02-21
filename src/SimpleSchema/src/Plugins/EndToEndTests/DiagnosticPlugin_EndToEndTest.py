# ----------------------------------------------------------------------
# |
# |  DiagnosticPlugin_EndToEndTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-08 11:36:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""End-to-end tests for DiagnosticPlugin"""

from pathlib import Path

from Common_Foundation import PathEx

from .TestHelpers import Test

# code_coverage: include = ../DiagnosticPlugin.py
# code_coverage: include = ../../SimpleSchema/Plugin.py


# ----------------------------------------------------------------------
def test_Standard(tmp_path):
    Test(
        "Diagnostic",
        tmp_path,
        PathEx.EnsureDir(Path(__file__).parent / "Results" / "DiagnosticPlugin"),
    )
