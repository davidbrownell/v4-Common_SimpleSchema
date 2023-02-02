# ----------------------------------------------------------------------
# |
# |  Element.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 07:11:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Element object"""

from abc import ABC
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import auto, Flag
from typing import Any, ClassVar, Generator, Iterator, Optional, Tuple, Union
from weakref import ref, ReferenceType

from Common_Foundation.Types import extensionmethod

from ....Common.Range import Range


# ----------------------------------------------------------------------
class VisitResult(Flag):
    """Result returned from Accept to control the visitation process"""

    Continue                                = 0

    SkipDetails                             = auto()
    SkipChildren                            = auto()

    Terminate                               = auto()

    SkipAll                                 = SkipDetails | SkipChildren


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Element(ABC):
    """Root for all entities processed by SimpleSchema"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    GenerateAcceptDetailsGeneratorItemsType = Union[
        "Element",
        ReferenceType["Element"],
        list["Element"],
        list[ReferenceType["Element"]],
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Data
    # |
    # ----------------------------------------------------------------------
    CHILDREN_NAME: ClassVar[str]            = "children"

    range: Range

    is_disabled: bool                                   = field(init=False, default=False)

    # ----------------------------------------------------------------------
    def Disable(self) -> None:
        if self.is_disabled:
            raise Exception("The element is already disabled.")

        object.__setattr__(self, "is_disabled", True)

    # ----------------------------------------------------------------------
    def Accept(
        self,
        visitor: Any,
        *,
        include_disabled: bool=False,
    ) -> VisitResult:
        if self.is_disabled and not include_disabled:
            return VisitResult.Continue

        method = getattr(visitor, "OnElement", self.__class__._GenericYieldFunc)  # pylint: disable=protected-access
        with method(self) as element_visit_result:
            if element_visit_result == VisitResult.Terminate:
                return element_visit_result

            if element_visit_result == VisitResult.SkipAll:
                return VisitResult.Continue

            method_name = "On{}".format(self.__class__.__name__)

            method = getattr(visitor, method_name, None)
            assert method is not None, method_name

            with method(self) as method_visit_result:
                if method_visit_result == VisitResult.Terminate:
                    return method_visit_result

                # Enumerate the details associated with the Element (if any)
                if not self.__class__._GetFirstVisitResult(method_visit_result, element_visit_result) & VisitResult.SkipDetails:  # pylint: disable=protected-access
                    accept_details = list(self._GenerateAcceptDetails())

                    if accept_details:
                        method = getattr(visitor, "OnElementDetails", self.__class__._GenericYieldFunc)  # pylint: disable=protected-access
                        with method(self) as details_visit_result:
                            if details_visit_result == VisitResult.Terminate:
                                return details_visit_result

                            if not self.__class__._GetFirstVisitResult(details_visit_result) & VisitResult.SkipDetails:  # pylint: disable=protected-access
                                method_name_prefix = "On{}__".format(self.__class__.__name__)

                                for detail_name, detail_value in accept_details:
                                    method_name = method_name_prefix + detail_name

                                    method = getattr(visitor, method_name, None)
                                    assert method is not None, method_name

                                    details_visit_result = method(
                                        detail_value,
                                        include_disabled=include_disabled,
                                    )

                                    if details_visit_result == VisitResult.Terminate:
                                        return details_visit_result

                # Enumerate the children associated with the Element (if any)
                if not self.__class__._GetFirstVisitResult(method_visit_result, element_visit_result) & VisitResult.SkipChildren:  # pylint: disable=protected-access
                    with self._GenerateAcceptChildren() as children:
                        if children:
                            method = getattr(visitor, "OnElementChildren", self.__class__._GenericYieldFunc)  # pylint: disable=protected-access
                            with method(self) as children_visit_result:
                                if children_visit_result == VisitResult.Terminate:
                                    return children_visit_result

                                if not self.__class__._GetFirstVisitResult(children_visit_result) & VisitResult.SkipChildren:  # pylint: disable=protected-access
                                    # Not using a generator here, as visiting the child may result in the
                                    # modification of its siblings. As a general rule, any modifications should
                                    # by done to siblings that follow this one rather than to those that come
                                    # before it.
                                    child_index = 0

                                    while child_index < len(children):
                                        child = children[child_index]
                                        child_index += 1

                                        child_visit_result = child.Accept(
                                            visitor,
                                            include_disabled=include_disabled,
                                        )

                                        if child_visit_result == VisitResult.Terminate:
                                            return child_visit_result

        return VisitResult.Continue

    # ----------------------------------------------------------------------
    # |
    # |  Protected Types
    # |
    # ----------------------------------------------------------------------
    _GenerateAcceptDetailsGeneratorType     = Generator[
        Tuple[str, GenerateAcceptDetailsGeneratorItemsType],
        None,
        None,
    ]

    _GenerateAcceptChildrenGeneratorType    = Iterator[Optional[list["Element"]]]

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def _GenericYieldFunc(*args, **kwargs) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield  # pragma: no cover

    # ----------------------------------------------------------------------
    @extensionmethod
    def _GenerateAcceptDetails(self) -> _GenerateAcceptDetailsGeneratorType:
        # Nothing by default
        if False:  # pylint: disable=using-constant-test
            yield

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> _GenerateAcceptChildrenGeneratorType:
        # No children by default
        yield None

    # ----------------------------------------------------------------------
    @staticmethod
    def _GetFirstVisitResult(
        *results: Optional[VisitResult],
    ) -> VisitResult:
        for result in results:
            if result is not None:
                return result

        return VisitResult.Continue
