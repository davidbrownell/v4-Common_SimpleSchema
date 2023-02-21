# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 10:38:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

import itertools

from dataclasses import dataclass
from typing import Any, cast, ClassVar, Tuple, Type as PythonType

from Common_Foundation.Types import DoesNotExist, overridemethod

from Common_FoundationEx.InflectEx import inflect

from .BasicType import BasicType
from .ReferenceType import ReferenceType

from ..Common.Element import Element

from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleType(BasicType):
    """A list of types"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Tuple"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (tuple, )

    types: list[ReferenceType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise Errors.TupleTypeNoTypes.Create(self.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def _display_type(self) -> str:
        display_values: list[str] = []

        for child_type in self.types:
            child_display = child_type.display_type

            if "{" in child_display and not (child_display.startswith("<") and child_display.endswith(">")):
                child_display = "<{}>".format(child_display)

            display_values.append(child_display)

        return "({}, )".format(", ".join(display_values))

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(TupleType, self)._GenerateAcceptDetails()

        yield "types", cast(list[Element], self.types)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: Tuple[Any, ...],
    ) -> Tuple[Any, ...]:
        tuple_items: list[Any] = []

        for child_type, child_expression_or_value in itertools.zip_longest(
            self.types,
            value,
            fillvalue=DoesNotExist.instance,
        ):
            if isinstance(child_type, DoesNotExist) or isinstance(child_expression_or_value, DoesNotExist):
                raise Exception(
                    Errors.tuple_type_item_mismatch.format(
                        value=inflect.no("tuple item", len(self.types)),
                        value_verb=inflect.plural_verb("was", len(self.types)),
                        found=inflect.no("tuple item", len(value)),
                        found_verb=inflect.plural_verb("was", len(value)),
                    ),
                )

            tuple_items.append(child_type.ToPython(child_expression_or_value))

        return tuple(tuple_items)
