# ----------------------------------------------------------------------
# |
# |  Type.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:49:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Type object"""

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Optional, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod, overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Element):
    """Abstract base class for types"""

    # ----------------------------------------------------------------------
    NAME = ""

    # ----------------------------------------------------------------------
    cardinality: Cardinality
    metadata: Optional[Metadata]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME

    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def display_name(self) -> str:
        raise Exception("Abstract property")

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
                self.range if isinstance(range, DoesNotExist) else range,
                self.cardinality if isinstance(cardinality, DoesNotExist) else cardinality,
                self.metadata if isinstance(metadata, DoesNotExist) else metadata,
            )

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def Resolve(self) -> Iterator["Type"]:
        yield self

    # ----------------------------------------------------------------------
    def ParseExpression(
        self,
        expression: Expression,
    ) -> Any:
        if self.cardinality.is_container:
            if not isinstance(expression, ListExpression):
                raise SimpleSchemaException("A list of items was expected.", expression.range)

            result = [self._ParseExpressionImpl(item) for item in expression.items]

        else:
            if isinstance(expression, ListExpression):
                raise SimpleSchemaException("A list of items was not expected.", expression.range)

            result = self._ParseExpressionImpl(expression)

        self.cardinality.ValidatePythonValue(result, expression.range)

        return result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
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
    @extensionmethod
    def _ParseExpressionImpl(
        self,
        expression: Expression,
    ) -> Any:
        if isinstance(expression, TupleExpression):
            raise Exception("TODO: Not implemented yet")

        assert False, expression  # pragma: no cover
