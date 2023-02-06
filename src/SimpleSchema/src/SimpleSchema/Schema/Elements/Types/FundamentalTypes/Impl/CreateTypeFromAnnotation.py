# ----------------------------------------------------------------------
# |
# |  CreateTypeFromAnnotation.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-05 12:25:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains methods the create a SimpleSchema Type from a python type annotation"""

from enum import EnumMeta
from types import GenericAlias, NoneType
from typing import Any, Type as PythonType, _BaseGenericAlias, _UnionGenericAlias  # type: ignore

from ..BooleanType import BooleanType
from ..EnumType import EnumType
from ..IntegerType import IntegerType
from ..NumberType import NumberType
from ..StringType import StringType

from ....Common.Cardinality import Cardinality

from ....Types.TupleType import TupleType
from ....Types.Type import Type
from ....Types.VariantType import VariantType

from ......Common import Errors
from ......Common.Range import Range


# ----------------------------------------------------------------------
def CreateTypeFromAnnotation(
    python_type_annotation: PythonType,
    *,
    has_default_value: bool,
) -> Type:
    cardinality_min: int = 0 if has_default_value else 1

    if isinstance(python_type_annotation, _UnionGenericAlias):
        # Optional or Variant
        types: list[Any] = []

        for contained_type in python_type_annotation.__args__:
            if contained_type is NoneType:
                cardinality_min = 0
            else:
                types.append(contained_type)

        if len(types) == 1:
            # Optional
            return CreateTypeFromAnnotation(types[0], has_default_value=False).Clone(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(0, 1),
            )

        # Variant
        return VariantType(
            Range.CreateFromCode(),
            Cardinality.CreateFromCode(cardinality_min, 1),
            None,
            [CreateTypeFromAnnotation(the_type, has_default_value=False) for the_type in types],
        )

    if (
        isinstance(python_type_annotation, GenericAlias)
        or isinstance(python_type_annotation, _BaseGenericAlias)
    ):
        if python_type_annotation.__origin__ == list:
            assert len(python_type_annotation.__args__) == 1, python_type_annotation.__args__

            return CreateTypeFromAnnotation(
                python_type_annotation.__args__[0],
                has_default_value=False,
            ).Clone(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(cardinality_min, None),
            )

        if python_type_annotation.__origin__ == tuple:
            return TupleType(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(cardinality_min, 1),
                None,
                [
                    CreateTypeFromAnnotation(the_type, has_default_value=False)
                    for the_type in python_type_annotation.__args__
                ],
            )

    range_value = Range.CreateFromCode()
    cardinality = Cardinality.CreateFromCode(cardinality_min, 1)

    if isinstance(python_type_annotation, EnumMeta):
        return EnumType(
            range_value,
            cardinality,
            None,
            [], 0, # The 2 values are ignored when the actual enum class is provided
            python_type_annotation,
        )

    if python_type_annotation == bool:
        return BooleanType(range_value, cardinality, None)

    if python_type_annotation == int:
        return IntegerType(range_value, cardinality, None)

    if python_type_annotation == float:
        return NumberType(range_value, cardinality, None)

    if python_type_annotation == str:
        return StringType(range_value, cardinality, None)

    raise Exception(Errors.create_type_from_annotation_invalid_type.format(value=python_type_annotation))
