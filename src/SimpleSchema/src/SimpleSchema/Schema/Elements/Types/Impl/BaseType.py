# ----------------------------------------------------------------------
# |
# |  BaseType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-13 13:52:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BaseType object"""

from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, ClassVar, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod

from ...Common.Element import Element
from ...Common.UniqueNameTrait import UniqueNameTrait

from ...Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BaseType(UniqueNameTrait, Element):
    """Abstract base class for BasicType and ComplexType"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                 = DoesNotExist.instance  # type: ignore

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME != DoesNotExist.instance, "Make sure to define the type's name."

    # ----------------------------------------------------------------------
    @cached_property
    def display_type(self) -> str:
        return self._display_type

    # ----------------------------------------------------------------------
    @abstractmethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @property
    @extensionmethod
    def _display_type(self) -> str:
        return self.__class__.NAME
