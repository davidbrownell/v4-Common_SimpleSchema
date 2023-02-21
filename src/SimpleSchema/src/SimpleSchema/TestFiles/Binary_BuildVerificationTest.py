# ----------------------------------------------------------------------
# |
# |  Binary_BuildVerificationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-02 11:27:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Build verification test for binaries"""

# Note that this file will be invoked outside of an activated environment and cannot take a dependency
# on anything in this repository or Common_Foundation.

import os
import subprocess
import stat
import sys
import textwrap

from pathlib import Path
from typing import List, Optional, Set


# ----------------------------------------------------------------------
def EntryPoint(
    args: List[str],
) -> int:
    if len(args) != 2:
        sys.stdout.write(
            textwrap.dedent(
                """\
                ERROR: Usage:

                    {} <temp_directory>

                """,
            ).format(
                args[0],
            ),
        )

        return -1

    temp_directory = Path(args[1])
    assert temp_directory.is_dir(), temp_directory

    # Get the SimpleSchema binary
    simple_schema_filename = Path(temp_directory) / "SimpleSchema"

    if not simple_schema_filename.is_file():
        potential_simple_schema_filename = simple_schema_filename.with_suffix(".exe")

        if potential_simple_schema_filename.is_file():
            simple_schema_filename = potential_simple_schema_filename

    if not simple_schema_filename.is_file():
        raise Exception("The filename '{}' does not exist.\n".format(simple_schema_filename))

    # https://github.com/actions/upload-artifact/issues/38
    # Permissions are not currently being saved when uploading artifacts, so they must be set here.
    # This will eventually be fixed, which is why I am placing the work around here rather than in
    # the artifact upload- or download-code.
    simple_schema_filename.chmod(stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR)

    # Execute Tests
    result = _ValidateGeneration(simple_schema_filename, temp_directory)
    if result != 0:
        return result

    return 0


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ValidateGeneration(
    simple_schema_filename: Path,
    temp_directory: Path,
) -> int:
    command_line = '"{exe}" Generate "{input}" "{output_dir}" --plugin Diagnostic --single-task --debug'.format(
        exe=simple_schema_filename,
        input=Path(__file__).parent,
        output_dir=temp_directory / "destination",
    )

    sys.stdout.write("Command Line: {}\n\n".format(command_line))

    result = subprocess.run(
        command_line,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    content = result.stdout.decode("utf-8")

    sys.stdout.write(content)

    return result.returncode


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(EntryPoint(sys.argv))
