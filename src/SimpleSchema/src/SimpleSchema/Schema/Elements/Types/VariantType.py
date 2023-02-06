# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 12:09:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Callable, cast, ClassVar, Tuple, Type as PythonType, Union

from Common_Foundation.Types import overridemethod

from .Type import Type

from ..Common.Element import Element

from ..Expressions.Expression import Expression

from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariantType(Type):
    """A list of types"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Variant"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    types: list[Type]

    _to_python_func: Callable[[Union[Expression, Any]], Any]                = field(init=False, compare=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if len(self.types) < 2:
            raise Errors.VariantTypeNotEnoughTypes.Create(self.range)

        has_parent_cardinality = not self.cardinality.is_single
        has_child_cardinality = False

        for the_type in self.types:
            if isinstance(the_type, VariantType):
                raise Errors.VariantTypeNested.Create(the_type.range)

            if not the_type.cardinality.is_single:
                if has_parent_cardinality:
                    raise Errors.VariantTypeCardinality.Create(the_type.cardinality.range)

                has_child_cardinality = True

        # If there are child cardinalities involved, we want to completely replace
        # the default ToPython  method (which checks cardinality) with the one that
        # is custom to variant types (which defer cardinality checks to the subtypes themselves).
        if has_child_cardinality:
            to_python_func = lambda expression_or_value: (
                self._ToPythonImpl(
                    expression_or_value,
                    lambda the_type: the_type.ToPython(expression_or_value),
                )
            )
        else:
            to_python_func = super(VariantType, self).ToPython

        object.__setattr__(self, "_to_python_func", to_python_func)

        super(VariantType, self).__post_init__()

    # ----------------------------------------------------------------------
    @overridemethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        return self._to_python_func(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def _display_name(self) -> str:
        return "({})".format(" | ".join(the_type.display_name for the_type in self.types))

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(VariantType, self)._GenerateAcceptDetails()

        yield "types", cast(list[Element], self.types)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Union[Expression, Any],
    ) -> Any:
        # If here, it means that that this element's cardinality was set and none
        # of the contained cardinalities were set.
        assert not self.cardinality.is_single or all(the_type.cardinality.is_single for the_type in self.types)

        return self._ToPythonImpl(
            value,
            lambda the_type: the_type.ItemToPython(value),
        )

    # ----------------------------------------------------------------------
    def _ToPythonImpl(
        self,
        expression_or_value: Union[Expression, Any],
        to_python_func: Callable[[Type], Any],
    ) -> Any:
        for the_type in self.types:
            try:
                return to_python_func(the_type)
            except:  # pylint: disable=bare-except
                # This type didn't match, try the next one
                pass

        if isinstance(expression_or_value, Expression):
            raise Errors.VariantTypeInvalidValue.Create(
                expression_or_value.range,
                expression=expression_or_value.NAME,
                type=self.display_name,
            )

        raise Exception(
            Errors.variant_type_invalid_value.format(
                python_type=type(expression_or_value).__name__,
                type=self.display_name,
            ),
        )
