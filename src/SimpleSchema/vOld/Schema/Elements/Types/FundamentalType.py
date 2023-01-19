# ----------------------------------------------------------------------
# |
# |  FundamentalType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-09 15:12:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FundamentalDefinition and FundamentalType objects"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple, Type as TypeOf, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod, overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.FundamentalExpression import Expression, FundamentalExpression

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Constraint(object):
    """Abstract base class for an object that is able to validate that an instance of a type meets a set of constraints corresponding to the type"""

    # ----------------------------------------------------------------------
    _expected_python_types: Tuple[TypeOf, ...]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs) -> "Constraint":
        # pylint has a hard time with dataclass hierarchies where derived classes overload base members
        # and initialize them by default. Using this method will work around those pylint errors.
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        pass

    # ----------------------------------------------------------------------
    def __call__(
        self,
        value: Any,
    ) -> Any:
        if not isinstance(value, self._expected_python_types):  # pylint: disable=isinstance-second-argument-not-valid-type
            raise Exception("'{}' is not {}".format(value,  ", ".join(self._expected_python_types)))

        return self._ValidateImpl(value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @extensionmethod
    def _ValidateImpl(
        self,
        value: Any,
    ) -> Any:
        # No additional validation is performed
        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FundamentalType(Type):
    """Abstract base class for fundamental types"""

    CONSTRAINT_TYPE                         = None
    EXPRESSION_TYPES                        = DoesNotExist.instance

    # ----------------------------------------------------------------------
    constraint: Constraint

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        range: Range,  # pylint: disable=redefined-builtin
        cardinality: Cardinality,
        metadata: Optional[Metadata],
        *args,
        **kwargs,
    ) -> "FundamentalType":
        assert cls.CONSTRAINT_TYPE is not None

        return cls(
            range,
            cardinality,
            metadata,
            cls.CONSTRAINT_TYPE(*args, **kwargs),  # type: ignore  # pylint: disable=not-callable
        )

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.CONSTRAINT_TYPE is not None
        assert self.EXPRESSION_TYPES is not DoesNotExist.instance

    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def display_name(self) -> str:
        return self.NAME

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateAcceptReferenceDetails(self) -> Element:
        return self

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        raise Exception("This should never be called on FundamentalType instances.")

    # ----------------------------------------------------------------------
    @overridemethod
    def _ParseExpressionImpl(
        self,
        expression: Expression,
    ) -> Any:
        if not isinstance(expression, FundamentalExpression):
            return super(FundamentalType, self)._ParseExpressionImpl(expression)

        supported_expressions: Union[None, TypeOf[FundamentalExpression], Tuple[TypeOf[FundamentalExpression], ...]] = self.EXPRESSION_TYPES  # type: ignore

        if supported_expressions is None:
            raise SimpleSchemaException(
                "The type '{}' does not support runtime expressions.".format(self.NAME),
                expression.range,
            )

        if not isinstance(expression, supported_expressions):  # type: ignore  # pylint: disable=isinstance-second-argument-not-valid-type
            raise SimpleSchemaException(
                "A {} expression was not expected.".format(expression.NAME),
                expression.range,
            )

        return self.constraint(expression.value)
