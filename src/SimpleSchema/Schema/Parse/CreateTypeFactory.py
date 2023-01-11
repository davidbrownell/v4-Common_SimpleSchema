# ----------------------------------------------------------------------
# |
# |  CreateTypeFactory.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-06 12:50:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that creates type factories"""

import itertools

from dataclasses import fields, MISSING
from enum import EnumMeta
from types import NoneType
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Type as TypeOf, _BaseGenericAlias, _UnionGenericAlias  # type: ignore

from Common_Foundation.Types import DoesNotExist

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.Expression import Expression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
def CreateTypeFactory(
    type_class: TypeOf[Type],
) -> Callable[[Range, Cardinality, Optional[Metadata]], Type]:
    return lambda range_value, cardinality, metadata: _CreateType(
        type_class,
        range_value,
        cardinality,
        metadata,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CreateType(
    type_class: TypeOf[Type],
    range_value: Range,
    cardinality: Cardinality,
    metadata: Optional[Metadata],
) -> Type:
    construct_args: Dict[str, Any] = {
        "range": range_value,
        "cardinality": cardinality,
        "metadata": metadata,
    }

    if metadata is None:
        pop_metadata_item_func = lambda name: None
    else:
        pop_metadata_item_func = lambda name: metadata.items.pop(name, None)  # type: ignore

    for field in fields(type_class):
        if not field.init:
            continue

        if field.name in construct_args:
            continue

        metadata_item = pop_metadata_item_func(field.name)

        if metadata_item is None:
            metadata_item_expression = None
            metadata_item_expression_range = range_value
        else:
            metadata_item_expression = metadata_item.value
            metadata_item_expression_range = metadata_item.value.range

        metadata_value = _CreateExpressionConverter(
            field.type,
            has_default_value=field.default is not MISSING,
        )(
            metadata_item_expression,
            metadata_item_expression_range,
        )

        if (
            metadata_value is not None
            or (field.default is MISSING and field.default_factory is MISSING)
        ):
            construct_args[field.name] = metadata_value

    if metadata is not None and not metadata.items:
        construct_args["metadata"] = None
        metadata = None

    return type_class(**construct_args)


# ----------------------------------------------------------------------
def _CreateExpressionConverter(
    expected_type: Any,
    *,
    has_default_value: bool,
    no_exceptions: bool=False,
) -> Callable[[Optional[Expression], Range], Any]:
    allow_none = has_default_value

    if isinstance(expected_type, _UnionGenericAlias):
        has_none_type = False
        types: List[Any] = []

        for contained_type in expected_type.__args__:
            if contained_type is NoneType:
                has_none_type = True
            else:
                types.append(contained_type)

        allow_none = has_none_type

        if len(types) == 1:
            # We are looking at an Optional type
            assert allow_none
            expected_type = types[0]

        else:
            # We are looking at an Union type
            union_converters = [
                _CreateExpressionConverter(
                    the_type,
                    has_default_value=False,
                    no_exceptions=True,
                )
                for the_type in types
            ]

            # ----------------------------------------------------------------------
            def VariantImpl(
                expression: Optional[Expression],
                default_expression_range: Range,
            ) -> Any:
                if expression is None:
                    if allow_none:
                        return None

                    error_name = "None"
                    error_range = default_expression_range

                else:
                    for union_converter in union_converters:
                        result = union_converter(expression, expression.range)
                        if result is not DoesNotExist.instance:
                            return result

                    error_name = expression.NAME
                    error_range = expression.range

                if no_exceptions:
                    return DoesNotExist.instance

                raise _CreateError("Union", error_name, error_range)

            # ----------------------------------------------------------------------

            return VariantImpl

    converters: Dict[TypeOf[Expression], Callable[[Expression], Any]] = {}

    if isinstance(expected_type, _BaseGenericAlias):
        if expected_type.__origin__ == list:
            assert len(expected_type.__args__) == 1, expected_type.__args__

            item_converter = _CreateExpressionConverter(
                expected_type.__args__[0],
                has_default_value=False,
            )

            converters[ListExpression] = lambda expression: [
                item_converter(item, item.range)
                for item in cast(ListExpression, expression).items
            ]

        elif expected_type.__origin__ == tuple:
            item_converters = [
                _CreateExpressionConverter(
                    arg,
                    has_default_value=False,
                )
                for arg in expected_type.__args__
            ]

            # ----------------------------------------------------------------------
            def TupleConverter(
                expression: Expression,
            ) -> Tuple[Any, ...]:
                values: List[Any] = []

                for item_converter, item_expression in itertools.zip_longest(
                    item_converters,
                    cast(TupleExpression, expression).expressions,
                    fillvalue=DoesNotExist.instance,
                ):
                    if isinstance(item_converter, DoesNotExist):
                        assert not isinstance(item_expression, DoesNotExist)
                        raise SimpleSchemaException("Too many tuple expressions were encountered.", item_expression.range)

                    if isinstance(item_expression, DoesNotExist):
                        raise SimpleSchemaException("Not enough tuple expressions were found.", expression.range)

                    values.append(item_converter(item_expression, item_expression.range))

                return tuple(values)

            # ----------------------------------------------------------------------

            converters[TupleExpression] = TupleConverter

    elif isinstance(expected_type, EnumMeta):
        # ----------------------------------------------------------------------
        def EnumFromString(
            value: str,
            range_value: Range,
        ) -> Any:
            # Search by enum name
            for enum_value in expected_type:            # type: ignore
                if enum_value.name == value:            # type: ignore
                    return value

            # Search by enum value
            for enum_value in expected_type:            # type: ignore
                if enum_value.value == value:           # type: ignore
                    return value

            if no_exceptions:
                return DoesNotExist.instance

            raise _CreateError("Enum", "'{}'".format(value), range_value)

        # ----------------------------------------------------------------------

        converters[StringExpression] = lambda expression: EnumFromString(cast(StringExpression, expression).value, expression.range)
        converters[IntegerExpression] = lambda expression: EnumFromString("Value{}".format(cast(IntegerExpression, expression).value), expression.range)

    elif expected_type == bool:
        converters[BooleanExpression] = lambda expression: cast(BooleanExpression, expression).value

    elif expected_type == int:
        converters[IntegerExpression] = lambda expression: cast(IntegerExpression, expression).value

    elif expected_type == float:
        converters[NumberExpression] = lambda expression: cast(NumberExpression, expression).value
        converters[IntegerExpression] = lambda expression: float(cast(IntegerExpression, expression).value)

    elif expected_type == str:
        converters[StringExpression] = lambda expression: cast(StringExpression, expression).value

    else:
        raise Exception("'{}' is not a supported python type.".format(expected_type))

    assert converters

    # ----------------------------------------------------------------------
    def Impl(
        expression: Optional[Expression],
        default_expression_range: Range,
    ) -> Any:
        if expression is None:
            if allow_none:
                return None

            if no_exceptions:
                return DoesNotExist.instance

            raise _CreateError(next(iter(converters.keys())).NAME, "None", default_expression_range)

        converter = converters.get(type(expression), None)

        if converter is None:
            if no_exceptions:
                return DoesNotExist.instance

            raise _CreateError(
                next(iter(converters.keys())).NAME,
                "a '{}' expression".format(expression.NAME),
                expression.range,
            )

        return converter(expression)

    # ----------------------------------------------------------------------

    return Impl


# ----------------------------------------------------------------------
def _CreateError(
    expected_type_desc: str,
    actual_type_desc: str,
    expression_range: Range,
) -> SimpleSchemaException:
    return SimpleSchemaException(
        "A '{}' expression was expected but {} was found.".format(
            expected_type_desc,
            actual_type_desc,
        ),
        expression_range,
    )
