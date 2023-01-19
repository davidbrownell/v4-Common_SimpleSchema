# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-02 18:00:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Implements an end-to-end Parse method"""

from pathlib import Path
from typing import Any, Callable, cast, Dict, Union

from Common_Foundation.Streams.DoneManager import DoneManager

from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.Expression import Expression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement

from SimpleSchema.Schema.Parse.ANTLR import Parse as ANTLRParseFunc
from SimpleSchema.Schema.Parse.TypeResolver import Resolve as ResolveTypes


# ----------------------------------------------------------------------
def Parse(
    dm: DoneManager,
    workspaces: Dict[
        Path,
        Dict[
            Path,
            Callable[[], str],
        ],
    ],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=False,
) -> Union[
    Dict[Path, Exception],
    Dict[Path, RootStatement],
]:
    # Get the basic elements
    initial_results = ANTLRParseFunc(
        dm,
        workspaces,
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    roots: Dict[Path, RootStatement] = {}
    exceptions: Dict[Path, Exception] = {}

    for workspace_results in initial_results.values():
        for filename, result in workspace_results.items():
            if isinstance(result, RootStatement):
                assert filename not in roots, filename
                roots[filename] = result
            elif isinstance(result, Exception):
                assert filename not in exceptions, filename
                exceptions[filename] = result
            else:
                assert False, result  # pragma: no cover

    if dm.result != 0:
        assert exceptions is not None

        if len(exceptions) == 1 and raise_if_single_exception:
            raise next(iter(exceptions.values()))

        return exceptions

    results = ResolveTypes(
        dm,
        roots,
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    if dm.result != 0:
        assert results is not None
        assert all(isinstance(value, Exception) for value in results.values())
        return cast(Dict[Path, Exception], results)

    return roots
