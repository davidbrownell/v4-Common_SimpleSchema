# ----------------------------------------------------------------------
# |
# |  TestHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-08 08:34:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Helpers for Plugin-based end-to-end tests"""

import runpy
import sys
import textwrap

from difflib import Differ
from pathlib import Path
from unittest.mock import patch

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation import TextwrapEx


# ----------------------------------------------------------------------
def Test(
    plugin_name: str,
    output_dir: Path,
    compare_dir: Path,
    *additional_command_line_args: str,
) -> None:
    with ExitStack(lambda: PathEx.RemoveTree(output_dir)):
        # Execute SimpleSchema

        # ----------------------------------------------------------------------
        def PatchedExit(
            result: int,
        ) -> None:
            assert result == 0

        # ----------------------------------------------------------------------

        with patch.object(sys, "exit", PatchedExit):
            src_root = PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)

            sys.argv = [
                "SimpleSchema",
                "Generate",
                str(PathEx.EnsureDir(src_root / "src" / "SimpleSchema" / "TestFiles")),
                str(output_dir),
                "--plugin", plugin_name,
                "--single-task",
                "--debug",
            ] + list(additional_command_line_args)

            runpy._run_module_as_main("src.EntryPoint")  # type: ignore  # pylint: protected-access

        # Compare the output
        output_files: dict[str, Path] = {
            filename.name: filename
            for filename in output_dir.iterdir()
            if filename.is_file() and not filename.name.endswith("ConditionalInvocationQueryMixin.data")
        }

        expected_files: dict[str, Path] = {
            filename.name : filename
            for filename in compare_dir.iterdir()
            if filename.is_file()
        }

        missing: list[str] = []
        unexpected: list[str] = []
        mismatches: dict[str, str] = {}

        for name, output_filename in output_files.items():
            expected_filename = expected_files.pop(name, None)
            if expected_filename is None:
                unexpected.append(name)
                continue

            # Compare
            with output_filename.open() as f:
                output_content = f.read().replace("\r\n", "\n")

            with expected_filename.open() as f:
                expected_content = f.read().replace("\r\n", "\n")

            if output_content != expected_content:
                diff = "".join(
                    Differ().compare(
                        expected_content.splitlines(True),
                        output_content.splitlines(True),
                    ),
                )

                mismatches[name] = diff

        for name in expected_files.keys():
            missing.append(name)

        error_message_parts: list[str] = []

        if missing:
            error_message_parts.append(
                textwrap.dedent(
                    """\
                    These files were not found:
                    {}

                    """,
                ).format("\n".join("    - {}".format(name) for name in missing)),
            )

        if unexpected:
            error_message_parts.append(
                textwrap.dedent(
                    """\
                    These files were missing:
                    {}

                    """,
                ).format("\n".join("    - {}".format(name) for name in unexpected)),
            )

        if mismatches:
            error_message_parts.append(
                textwrap.dedent(
                    """\
                    These files did not match:
                    {}

                    """,
                ).format(
                    TextwrapEx.Indent(
                        "\n".join(
                            textwrap.dedent(
                                """\
                                {}
                                    {}

                                """,
                            ).format(
                                name,
                                TextwrapEx.Indent(diff.rstrip(), 4, skip_first_line=True),
                            )
                            for name, diff in mismatches.items()
                        ).rstrip(),
                        4,
                    ),
                ),
            )

        if error_message_parts:
            errors = "\n\n{}".format("".join(error_message_parts).rstrip())
            assert False, errors
