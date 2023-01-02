# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 10:52:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

import re

from abc import ABC
from contextlib import contextmanager
from typing import Iterator, Optional

from Common_Foundation.Types import extensionmethod

from SimpleSchema.Schema.Elements.Common.Element import Element, VisitResult


# ----------------------------------------------------------------------
class Visitor(ABC):
    """Visitor base class"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    METHOD_REGEX                            = re.compile("^On(?P<object_name>.+)$")
    DETAILS_REGEX                           = re.compile("^On(?P<object_name>.+?)__(?P<member_name>.+)$")

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def OnElement(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def OnElementDetails(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def OnElementChildren(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    # @extensionmethod
    # @contextmanager
    # def On<Element Name>(self, element: <Element Type>) -> Iterator[Optional[VisitResult]]:
    #     ...

    # ----------------------------------------------------------------------
    # @extensionmethod
    # @contextmanager
    # def On<Element Name>__<Detail Name>(self, value: <Detail Value Type>, *, include_disabled: bool) -> Optional[VisitResult]:
    #     ...
