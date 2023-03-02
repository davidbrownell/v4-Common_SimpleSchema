# ----------------------------------------------------------------------
# |
# |  setup.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-31 08:36:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Setup for SimpleSchema"""

import datetime
import sys
import textwrap

from pathlib import Path
from typing import Tuple

from cx_Freeze import setup, Executable

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Shell.All import CurrentShell
from Common_Foundation import SubprocessEx


# ----------------------------------------------------------------------
_this_dir                                   = Path(__file__).parent
_name                                       = _this_dir.name

_initial_year                               = 2023


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(_this_dir / "src" / "EntryPoint")))
with ExitStack(lambda: sys.path.pop(0)):
    # We have to import in this way to get the proper doc string from __main__.py
    import __main__ as SimpleSchemaMain


# ----------------------------------------------------------------------
def _GetVersion() -> str:
    result = SubprocessEx.Run(
        'AutoSemVer{ext} --no-branch-name --no-metadata --quiet'.format(
            ext=CurrentShell.script_extensions[0],
        ),
        cwd=_this_dir,
    )

    assert result.returncode == 0, result.output
    return result.output.strip()

_version = _GetVersion()
del _GetVersion


# ----------------------------------------------------------------------
# Create the year suffix
_year = datetime.datetime.now().year

if _year == _initial_year:
    _year_suffix = ""  # pylint: disable=invalid-name
else:
    if _year < 2100:
        _year = _year % 100

    _year_suffix = "-" + str(_year)  # pylint: disable=invalid-name


# ----------------------------------------------------------------------
include_files: list[Tuple[str, str]] = []

for child in Path("src/Plugins").iterdir():
    if (
        not child.is_file
        or child.suffix != ".py"
        or child.stem == "__init__"
    ):
        continue

    include_files.append(
        (
            str(child),
            str(Path(*child.parts[1:])),
        ),
    )


# ----------------------------------------------------------------------
setup(
    name=_name,
    version=_version,
    description=SimpleSchemaMain.__doc__,
    executables=[
        Executable(
            PathEx.EnsureFile(Path(__file__).parent / "src" / "EntryPoint" / "__main__.py"),
            base=None,
            copyright=textwrap.dedent(
                """\
                Copyright David Brownell {year}{year_suffix}
                Distributed under the Boost Software License, Version 1.0. See
                copy at http://www.boost.org/LICENSE_1_0.txt.
                """,
            ).format(
                year=str(_initial_year),
                year_suffix=_year_suffix,
            ),
            # icon=<icon_filename>
            target_name=_name,
            # trademarks="",
        ),
    ],
    options={
        "build_exe": {
            "excludes": [
                "tcl",
                "tkinter",
            ],
            "no_compress": False,
            "optimize": 0,
            "packages": [
                "antlr_denter",
                "rtyaml",
            ],
            "include_files": include_files,
        },
    },
)
