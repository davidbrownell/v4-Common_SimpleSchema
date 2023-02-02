# ----------------------------------------------------------------------
# |
# |  FundamentalTypeCreator.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 16:07:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
from dataclasses import fields, MISSING
from enum import EnumMeta
from types import GenericAlias, NoneType
from typing import Any, Optional, Type as PythonType, _BaseGenericAlias, _UnionGenericAlias  # type: ignore

from Common_Foundation.Types import DoesNotExist

from .BooleanType import BooleanType
from .EnumType import EnumType
from .IntegerType import IntegerType
from .NumberType import NumberType
from .StringType import StringType

from ..FundamentalType import FundamentalType
from ..TupleType import TupleType
from ..Type import Type
from ..VariantType import VariantType

from ...Common.Cardinality import Cardinality
from ...Common.Metadata import Metadata, MetadataItem

from .....Common import Errors
from .....Common.Range import Range
from .....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
def CreateFromMetadata(
    the_type: PythonType[FundamentalType],
    range_value: Range,
    cardinality: Cardinality,
    metadata: Optional[Metadata],
) -> FundamentalType:
    if metadata is None:
        pop_metadata_item_func = lambda name: DoesNotExist.instance
    else:
        pop_metadata_item_func = lambda name: metadata.items.pop(name, DoesNotExist.instance)

    construct_args: dict[str, Any] = {
        "range": range_value,
        "cardinality": cardinality,
        "metadata": metadata,
    }

    for field in fields(the_type):
        if not field.init:
            continue

        if field.name in construct_args:
            continue

        metadata_item = pop_metadata_item_func(field.name)
        if metadata_item == DoesNotExist.instance:
            continue

        assert isinstance(metadata_item, MetadataItem)

        metadata_value = _CreateDefaultType(
            field.type,
            has_default_value=field.default is not MISSING,
        ).ToPython(metadata_item.expression)

        if (
            metadata_value is not None
            or (field.default is MISSING and field.default_factory is MISSING)
        ):
            construct_args[field.name] = metadata_value

    if metadata is not None and not metadata.items:
        construct_args["metadata"] = None

    try:
        return the_type(**construct_args)
    except Exception as ex:
        raise SimpleSchemaException(
            metadata.range if metadata is not None else range_value,
            str(ex),
        ) from ex


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CreateDefaultType(
    expected_type: Any,
    *,
    has_default_value: bool,
) -> Type:
    cardinality_min: int = 0 if has_default_value else 1

    if isinstance(expected_type, _UnionGenericAlias):
        types: list[Any] = []

        for contained_type in expected_type.__args__:
            if contained_type is NoneType:
                cardinality_min = 0
            else:
                types.append(contained_type)

        if len(types) == 1:
            # We are looking at an Optional type
            return _CreateDefaultType(types[0], has_default_value=False).Clone(
                cardinality=Cardinality.CreateFromCode(0, 1),
            )

        # We are looking at a Variant type
        return VariantType(
            Range.CreateFromCode(),
            Cardinality.CreateFromCode(cardinality_min, 1),
            None,
            [_CreateDefaultType(the_type, has_default_value=False) for the_type in types],
        )

    if (
        isinstance(expected_type, GenericAlias)
        or isinstance(expected_type, _BaseGenericAlias)
    ):
        if expected_type.__origin__ == list:
            assert len(expected_type.__args__) == 1, expected_type.__args__

            return _CreateDefaultType(expected_type.__args__[0], has_default_value=False).Clone(
                cardinality=Cardinality.CreateFromCode(cardinality_min, None),
            )

        if expected_type.__origin__ == tuple:
            return TupleType(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(cardinality_min, 1),
                None,
                [
                    _CreateDefaultType(the_type, has_default_value=False)
                    for the_type in expected_type.__args__
                ],
            )

    range_value = Range.CreateFromCode()
    cardinality = Cardinality.CreateFromCode(cardinality_min, 1)

    if isinstance(expected_type, EnumMeta):
        return EnumType(
            range_value,
            cardinality,
            None,
            # Note that the following 2 values are ignored when the enum type is provided, but need
            # to be present to construct the instance.
            [e.name for e in expected_type],  # type: ignore
            0,
            expected_type,
        )

    if expected_type == bool:
        return BooleanType(range_value, cardinality, None)

    if expected_type == int:
        return IntegerType(range_value, cardinality, None)

    if expected_type == float:
        return NumberType(range_value, cardinality, None)

    if expected_type == str:
        return StringType(range_value, cardinality, None)

    raise Exception(Errors.fundamental_type_creator_invalid_type.format(value=expected_type))
