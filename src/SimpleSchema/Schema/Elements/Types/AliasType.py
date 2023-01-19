# ----------------------------------------------------------------------
# |
# |  AliasType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-09 15:02:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AliasType object"""

from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import Iterator

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AliasType(Type):
    """A type that references another type"""

    # ----------------------------------------------------------------------
    NAME = "Alias"

    # ----------------------------------------------------------------------
    name: Identifier
    type: Type

    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def display_name(self) -> str:
        return "Alias -> {}".format(self.type.display_name)

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def Resolve(self) -> Iterator[Type]:
        try:
            with self.type.Resolve() as resolved_type:
                yield resolved_type
        except SimpleSchemaException as ex:
            ex.ranges.insert(0, self.range)
            raise

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "type", self.type

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateAcceptReferenceDetails(self) -> Element:
        return self.type._CreateAcceptReferenceDetails()  # pylint: disable=protected-access

# ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        raise Exception("This should never be called on AliasType instances.")

    # ----------------------------------------------------------------------
    @overridemethod
    def _ParseExpressionImpl(self, *args, **kwargs):
        raise Exception("An alias cannot be created from an expression.")
