# ----------------------------------------------------------------------
# |
# |  ExecuteInParallel.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-08 14:06:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExecuteInParallel function"""

from pathlib import Path
from typing import Callable, cast, Optional, TypeVar, Union

from Common_Foundation.Streams.DoneManager import DoneManager

from Common_FoundationEx import ExecuteTasks


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
ExecuteInParallelInputT                     = TypeVar("ExecuteInParallelInputT")
ExecuteInParallelOutputT                    = TypeVar("ExecuteInParallelOutputT")


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def ExecuteInParallel(
    dm: DoneManager,
    heading: str,
    items: dict[Path, ExecuteInParallelInputT],
    func: Callable[[ExecuteInParallelInputT, ExecuteTasks.Status], ExecuteInParallelOutputT],
    *,
    quiet: bool,
    max_num_threads: Optional[int],
    raise_if_single_exception: bool,
    num_steps: Optional[int]=None,
) -> Union[
    dict[Path, Exception],
    dict[Path, ExecuteInParallelOutputT],
]:
    # ----------------------------------------------------------------------
    def Execute(
        context: ExecuteInParallelInputT,
        on_simple_status_func: Callable[[str], None],  # pylint: disable=unused-argument
    ) -> tuple[
        Optional[int],
        ExecuteTasks.TransformStep2FuncType[Union[Exception, ExecuteInParallelOutputT]],
    ]:
        # ----------------------------------------------------------------------
        def Impl(
            status: ExecuteTasks.Status,
        ) -> tuple[Union[Exception, ExecuteInParallelOutputT], Optional[str]]:
            return func(context, status), None

        # ----------------------------------------------------------------------

        return num_steps, Impl

    # ----------------------------------------------------------------------

    exceptions: dict[Path, Exception] = {}
    results: dict[Path, ExecuteInParallelOutputT] = {}

    for filename, result in zip(
        items.keys(),
        ExecuteTasks.Transform(
            dm,
            heading,
            [
                ExecuteTasks.TaskData(str(filename), context)
                for filename, context in items.items()
            ],
            Execute,
            quiet=quiet,
            max_num_threads=max_num_threads,
            return_exceptions=True,
        ),
    ):
        if isinstance(result, Exception):
            exceptions[filename] = result
        else:
            results[filename] = cast(ExecuteInParallelOutputT, result)

    if raise_if_single_exception and exceptions and len(exceptions) == 1:
        raise next(iter(exceptions.values()))

    return exceptions or results
