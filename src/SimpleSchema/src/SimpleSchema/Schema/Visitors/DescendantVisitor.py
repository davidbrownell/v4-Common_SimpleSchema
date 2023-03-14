# ----------------------------------------------------------------------
# |
# |  DescendantVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-14 11:24:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DescendantVisitor object"""

from contextlib import contextmanager
from typing import Callable, Iterator, Optional

from Common_Foundation.Types import overridemethod

from .NonRecursiveVisitor import NonRecursiveVisitor, VisitResult

from ..Elements.Common.Element import Element


# ----------------------------------------------------------------------
class DescendantVisitor(NonRecursiveVisitor):
    # ----------------------------------------------------------------------
    @classmethod
    def EnumDescendants(
        cls,
        element: Element,
        on_element_func: Callable[[Element], Optional[VisitResult]],
    ) -> bool:
        return element.Accept(cls(on_element_func)) == VisitResult.Continue

    # ----------------------------------------------------------------------
    def __init__(
        self,
        on_element_func: Callable[[Element], Optional[VisitResult]],
    ):
        super(DescendantVisitor, self).__init__()

        self._on_element_func               = on_element_func

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        with super(DescendantVisitor, self).OnElement(element) as visit_result:
            if visit_result is not None and visit_result != VisitResult.Continue:
                yield visit_result
                return

            visit_result = self._on_element_func(element)
            if visit_result is not None and visit_result != VisitResult.Continue:
                yield visit_result
                return

            yield
