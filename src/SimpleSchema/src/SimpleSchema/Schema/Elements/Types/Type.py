# ----------------------------------------------------------------------
# |
# |  Type.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 11:38:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Type object"""

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from types import NoneType
from typing import Any, ClassVar, Iterator, Optional, Tuple, Type as PythonType, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod, overridemethod

from ..Common.Cardinality import Cardinality
from ..Common.Element import Element
from ..Common.Metadata import Metadata

from ..Expressions.Expression import Expression
from ..Expressions.ListExpression import ListExpression
from ..Expressions.NoneExpression import NoneExpression

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Element):
    """Abstract base class for types supported by SimpleSchema"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = DoesNotExist.instance  # type: ignore
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = DoesNotExist.instance  # type: ignore

    cardinality: Cardinality
    metadata: Optional[Metadata]

    _single_item_type: Optional["Type"]     = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME != DoesNotExist.instance, "Make sure to define the type's name."
        assert self.SUPPORTED_PYTHON_TYPES != DoesNotExist.instance, "Make sure to define the supported python types."

        if self.cardinality.is_container:
            single_item_type = self.Clone(cardinality=Cardinality.CreateFromCode())
        else:
            single_item_type = None

        object.__setattr__(self, "_single_item_type", single_item_type)

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def Resolve(self) -> Iterator["Type"]:
        try:
            yield self
        except SimpleSchemaException as ex:
            ex.ranges.append(self.range)
            raise

    # ----------------------------------------------------------------------
    @cached_property
    def display_name(self) -> str:
        return "{}{}".format(self._display_name, self.cardinality)

    # ----------------------------------------------------------------------
    def Clone(
        self,
        *,
        range: Union[DoesNotExist, Range]=DoesNotExist.instance,  # pylint: disable=redefined-builtin
        cardinality: Union[DoesNotExist, Cardinality]=DoesNotExist.instance,
        metadata: Union[DoesNotExist, None, Metadata]=DoesNotExist.instance,
    ) -> "Type":
        with self.Resolve() as resolved_type:
            return resolved_type._CloneImpl(  # pylint: disable=protected-access
                resolved_type.range if isinstance(range, DoesNotExist) else range,
                resolved_type.cardinality if isinstance(cardinality, DoesNotExist) else cardinality,
                resolved_type.metadata if isinstance(metadata, DoesNotExist) else metadata,
            )

    # ----------------------------------------------------------------------
    @extensionmethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        self.cardinality.Validate(expression_or_value)

        if isinstance(expression_or_value, (NoneExpression, NoneType)):
            return None

        if isinstance(expression_or_value, ListExpression):
            try:
                return [self.ItemToPython(item) for item in expression_or_value.value]

            # This clause is only hit right now for tuples, which makes it difficult to unit test
            # within Type_UnitTest.py without recreating the tuple infrastructure there. Rather
            # than doing that, I've eliminated code coverage for these lines and ensured that
            # the scenario is covered in TupleType_UnitTest.py
            except SimpleSchemaException as ex:                             # pragma: no cover
                ex.ranges.append(expression_or_value.range)                 # pragma: no cover
                raise                                                       # pragma: no cover

        elif isinstance(expression_or_value, list):
            return [self.ItemToPython(item) for item in expression_or_value]

        return self.ItemToPython(expression_or_value)

    # ----------------------------------------------------------------------
    @extensionmethod
    def ItemToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        # ----------------------------------------------------------------------
        def Impl(
            value: Any,
        ) -> Any:
            if not isinstance(value, self.SUPPORTED_PYTHON_TYPES):  # pylint: disable=isinstance-second-argument-not-valid-type
                raise Exception(
                    Errors.type_validate_invalid_python_type.format(
                        python_type=type(value).__name__,
                        type=self.display_name,
                    ),
                )

            return self._ItemToPythonImpl(value)

        # ----------------------------------------------------------------------

        if isinstance(expression_or_value, Expression):
            try:
                return Impl(expression_or_value.value)
            except Exception as ex:
                raise SimpleSchemaException(expression_or_value.range, str(ex)) from ex

        return Impl(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @extensionmethod
    @property
    def _display_name(self) -> str:
        return self.NAME

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "cardinality", self.cardinality

        if self.metadata:
            yield "metadata", self.metadata

    # ----------------------------------------------------------------------
    @abstractmethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "Type":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def _ItemToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        raise Exception("Abstract method")  # pragma: no cover
