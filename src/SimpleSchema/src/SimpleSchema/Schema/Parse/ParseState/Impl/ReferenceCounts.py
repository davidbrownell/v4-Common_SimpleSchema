# ----------------------------------------------------------------------
# |
# |  ReferenceCounts.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-13 07:48:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ReferenceCount object"""

from collections import defaultdict
from dataclasses import dataclass, field
from functools import singledispatchmethod

from ....Elements.Common.Element import Element

from ....Elements.Statements.ItemStatement import ItemStatement
from ....Elements.Statements.StructureStatement import StructureStatement

from ....Elements.Types.FundamentalType import FundamentalType
from ....Elements.Types.ReferenceType import ReferenceType
from ....Elements.Types.StructureType import StructureType
from ....Elements.Types.TupleType import TupleType
from ....Elements.Types.VariantType import VariantType


# ----------------------------------------------------------------------
@dataclass
class ReferenceCounts(object):
    """Functionality that implements reference counting for applicable Elements"""

    # ----------------------------------------------------------------------
    _reference_counts: defaultdict[int, int]            = field(init=False, default_factory=lambda: defaultdict(lambda: 0))

    # ----------------------------------------------------------------------
    def Get(
        self,
        element: Element,
    ) -> int:
        return self._reference_counts.get(id(element), 0)

    # ----------------------------------------------------------------------
    @singledispatchmethod
    def Increment(
        self,
        element: Element,                   # pylint: disable=unused-argument
        *,
        shallow: bool=False,                # pylint: disable=unused-argument
        delta: int=1,                       # pylint: disable=unused-argument
    ) -> None:
        # By default, there is nothing to do
        pass

    # ----------------------------------------------------------------------
    @Increment.register
    def _(
        self,
        element: StructureStatement,
        *,
        shallow: bool=False,
        delta: int=1,
    ) -> None:
        self._Increment(element, delta)

        if shallow is False:
            for base_type in element.base_types:
                self.Increment(base_type, shallow=shallow, delta=delta)

            for child in element.children:
                if child.is_disabled:
                    continue

                if not isinstance(child, ItemStatement):
                    continue

                self.Increment(child.type, shallow=shallow, delta=delta)

    # ----------------------------------------------------------------------
    @Increment.register
    def _(
        self,
        element: FundamentalType,
        *,
        shallow: bool=False,
        delta: int=1,
    ) -> None:
        assert shallow is False
        self._Increment(element, delta)

    # ----------------------------------------------------------------------
    @Increment.register
    def _(
        self,
        element: ReferenceType,
        *,
        shallow: bool=False,
        delta: int=1,
    ) -> None:
        self._Increment(element, delta)
        self.Increment(element.type, shallow=shallow, delta=delta)

    # ----------------------------------------------------------------------
    @Increment.register
    def _(
        self,
        element: StructureType,
        *,
        shallow: bool=False,
        delta: int=1,
    ) -> None:
        self._Increment(element, delta)
        self.Increment(element.structure, shallow=shallow, delta=delta)

    # ----------------------------------------------------------------------
    @Increment.register
    def _(
        self,
        element: TupleType,
        *,
        shallow: bool=False,
        delta: int=1,
    ) -> None:
        assert shallow is False
        self._Increment(element, delta)

        for child_type in element.types:
            self.Increment(child_type, shallow=shallow, delta=delta)

    # ----------------------------------------------------------------------
    @Increment.register
    def _(
        self,
        element: VariantType,
        *,
        shallow: bool=False,
        delta: int=1,
    ) -> None:
        assert shallow is False
        self._Increment(element, delta)

        for child_type in element.types:
            self.Increment(child_type, shallow=shallow, delta=delta)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _Increment(
        self,
        element: Element,
        delta: int,
    ) -> None:
        if delta <= 0:
            raise ValueError("'delta' must be > 0")

        self._reference_counts[id(element)] += delta
