# ----------------------------------------------------------------------
# |
# |  SimpleSchema.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-11 13:42:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""BugBug"""

import os
import sys

from pathlib import Path
from typing import List

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation import SubprocessEx


# ----------------------------------------------------------------------
def Execute(
    args: List[str],
) -> int:
    src_root = PathEx.EnsureDir(Path(__file__).parent.parent / "src")

    prev_dir = Path.cwd()
    os.chdir(src_root)

    with ExitStack(lambda: os.chdir(prev_dir)):
        main_filename = Path("SimpleSchema") / "__main__.py"
        assert (src_root / main_filename).is_file(), src_root / main_filename

        command_line = 'python -m "{script}"{args}'.format(
            script=".".join(main_filename.parent.parts),
            args=" {}".format(" ".join('"{}"'.format(arg) for arg in args[1:])) if len(args) > 1 else "",
        )

        return SubprocessEx.Stream(command_line, sys.stdout)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(Execute(sys.argv))
