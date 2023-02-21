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
from typing import Any, cast, ClassVar, Tuple, Type as PythonType, Union, TYPE_CHECKING

from Common_Foundation.Types import overridemethod

from .BasicType import BasicType

from ..Common.Element import Element

from ..Expressions.Expression import Expression

from ....Common import Errors
from ....Common.SimpleSchemaException import SimpleSchemaException

if TYPE_CHECKING:
    from .ReferenceType import ReferenceType  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariantType(BasicType):
    """A list of types"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Variant"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    types: list["ReferenceType"]

    has_child_cardinality: bool                                             = field(init=False, compare=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if len(self.types) < 2:
            raise Errors.VariantTypeNotEnoughTypes.Create(self.range)

        has_child_cardinality = False

        for the_type in self.types:
            if isinstance(the_type, VariantType):
                raise Errors.VariantTypeNested.Create(the_type.range)

            if not the_type.cardinality.is_single:
                has_child_cardinality = True
                break

        object.__setattr__(self, "has_child_cardinality", has_child_cardinality)

        super(VariantType, self).__post_init__()

    # ----------------------------------------------------------------------
    def ToPythonReferenceOverride(
        self,
        reference: "ReferenceType",
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        # If here, the following matching cases may apply when the input is valid:
        #
        #   1) There are one ore more expression items and they correspond to a single subtype
        #   2) There are multiple expression items and they correspond to multiple subtypes

        if self.has_child_cardinality:
            # 1
            try:
                return self.ToPython(expression_or_value)
            except Exception:
                # No match
                pass

        # 2
        return reference.ToPythonImpl(expression_or_value)

    # ----------------------------------------------------------------------
    @overridemethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        # ----------------------------------------------------------------------
        def Impl(
            value: Any,
        ) -> Any:
            for sub_type in self.types:
                try:
                    return sub_type.ToPython(value)
                except:  # pylint: disable=bare-except
                    # The type did not match
                    pass

            # If here, we didn't find a matching type
            raise Exception(
                Errors.variant_type_invalid_value.format(
                    python_type=type(value).__name__,
                    type=self.display_type,
                ),
            )

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
    @cached_property
    @overridemethod
    def _display_type(self) -> str:
        display_values: list[str] = []

        for child_type in self.types:
            child_display = child_type.display_type

            if "{" in child_display and not (child_display.startswith("<") and child_display.endswith(">")):
                child_display = "<{}>".format(child_display)

            display_values.append(child_display)

        return "({})".format(" | ".join(display_values))

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(VariantType, self)._GenerateAcceptDetails()

        yield "types", cast(list[Element], self.types)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        raise Exception("This will never be called for variant types.")  # pragma: no cover
