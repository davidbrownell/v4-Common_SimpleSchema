# ----------------------------------------------------------------------
# |
# |  NonRecursiveVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-14 11:40:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NonRecursiveVisitor object"""

from contextlib import contextmanager
from typing import Iterator, Optional

from Common_Foundation.Types import overridemethod

from .Visitor import Visitor, VisitResult
from ..Elements.Common.Element import Element


# ----------------------------------------------------------------------
class NonRecursiveVisitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(NonRecursiveVisitor, self).__init__()

        self._visited: set[int]             = set()

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        with super(NonRecursiveVisitor, self).OnElement(element) as visit_result:
            if visit_result is not None:
                yield visit_result
                return

            visited_key = id(element)

            if visited_key in self._visited:
                yield VisitResult.SkipAll
                return

            self._visited.add(visited_key)
            yield
