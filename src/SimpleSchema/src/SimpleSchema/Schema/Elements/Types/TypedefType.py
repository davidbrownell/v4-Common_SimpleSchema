# ----------------------------------------------------------------------
# |
# |  TypedefType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 11:02:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypedefType object"""

from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import cast, ClassVar, Iterator, Tuple, Type as PythonType
from weakref import ref, ReferenceType

from Common_Foundation.Types import overridemethod

from .Type import Type

from ..Common.Element import Element
from ..Common.SimpleElement import SimpleElement
from ..Common.Visibility import Visibility

from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypedefType(Type):
    """A Type that references another type"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Typedef"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (object, )

    visibility: SimpleElement[Visibility]
    name: SimpleElement[str]
    type: Type

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def Resolve(self) -> Iterator[Type]:
        try:
            with self.type.Resolve() as resolved_type:
                yield resolved_type
        except SimpleSchemaException as ex:
            ex.ranges.append(self.range)
            raise

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def _display_name(self) -> str:
        return "(Typedef ({}) -> {})".format(self.name.value, self.type.display_name)

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(TypedefType, self)._GenerateAcceptDetails()

        yield "name", self.name
        yield "type", cast(ReferenceType[Element], ref(self.type))

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        # This code can't be tested, because Type will call Resolve before invoking CloneImpl.
        # The local implementation on Resolve makes sure that an instance different from this
        # one will be returned.
        raise Exception("This method should never be called for TypedefType instances.")  # pragma: no cover

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(self, *args, **kwargs):
        raise Exception("This method should never be called for TypedefType instances.")
