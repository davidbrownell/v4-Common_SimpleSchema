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
from typing import Any, Optional, Type as PythonType, _BaseGenericAlias, _UnionGenericAlias  # type: ignore

from ..BooleanType import BooleanType
from ..EnumType import EnumType
from ..IntegerType import IntegerType
from ..NumberType import NumberType
from ..StringType import StringType

from ....Common.Cardinality import Cardinality
from ....Common.SimpleElement import SimpleElement
from ....Common.Visibility import Visibility

from ....Types.BasicType import BasicType
from ....Types.ReferenceType import ReferenceType
from ....Types.TupleType import TupleType
from ....Types.VariantType import VariantType

from ......Common import Errors
from ......Common.Range import Range


# ----------------------------------------------------------------------
def CreateTypeFromAnnotation(
    python_type_annotation: PythonType,
    *,
    has_default_value: bool,
) -> ReferenceType:
    cardinality_min: int = 0 if has_default_value else 1
    cardinality_max: Optional[int] = 1

    basic_type: Optional[BasicType] = None

    if basic_type is None and isinstance(python_type_annotation, _UnionGenericAlias):
        # Optional or Variant
        types: list[Any] = []

        for contained_type in python_type_annotation.__args__:
            if contained_type is NoneType:
                cardinality_min = 0
            else:
                types.append(contained_type)

        if len(types) == 1:
            # Optional
            cardinality_min = 0
            python_type_annotation = types[0]

        else:
            # Variant
            basic_type = VariantType(
                Range.CreateFromCode(),
                [
                    CreateTypeFromAnnotation(the_type, has_default_value=False)
                    for the_type in types
                ],
            )

    while (
        basic_type is None
        and (
            isinstance(python_type_annotation, GenericAlias)
            or isinstance(python_type_annotation, _BaseGenericAlias)
        )
    ):
        if python_type_annotation.__origin__ == list:
            cardinality_max = None

            assert len(python_type_annotation.__args__) == 1, python_type_annotation.__args__
            python_type_annotation = python_type_annotation.__args__[0]

        elif python_type_annotation.__origin__ == tuple:
            basic_type = TupleType(
                Range.CreateFromCode(),
                [
                    CreateTypeFromAnnotation(the_type, has_default_value=False)
                    for the_type in python_type_annotation.__args__
                ],
            )

    if basic_type is None:
        if isinstance(python_type_annotation, EnumMeta):
            basic_type = EnumType(
                Range.CreateFromCode(),
                [], 0, # The 2 values are ignored when the actual enum class is provided
                python_type_annotation,
            )
        elif python_type_annotation == bool:
            basic_type = BooleanType(Range.CreateFromCode())
        elif python_type_annotation == int:
            basic_type = IntegerType(Range.CreateFromCode())
        elif python_type_annotation == float:
            basic_type = NumberType(Range.CreateFromCode())
        elif python_type_annotation == str:
            basic_type = StringType(Range.CreateFromCode())
        else:
            raise Exception(Errors.create_type_from_annotation_invalid_type.format(value=python_type_annotation))

    return ReferenceType.Create(
        Range.CreateFromCode(),
        SimpleElement[Visibility](Range.CreateFromCode(), Visibility.Private),
        SimpleElement[str](Range.CreateFromCode(), basic_type.NAME),
        basic_type,
        Cardinality.CreateFromCode(cardinality_min, cardinality_max),
        None,
        was_dynamically_generated=True,
    )
