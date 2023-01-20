# ----------------------------------------------------------------------
# |
# |  Type.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 11:38:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Type object"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Optional, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod, overridemethod

from ..Common.Cardinality import Cardinality
from ..Common.Element import Element
from ..Common.Metadata import Metadata

from ....Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Element):
    """Abstract base class for types supported by SimpleSchema"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = ""

    cardinality: Cardinality
    metadata: Optional[Metadata]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME != "", "Make sure to define the type's name."

    # ----------------------------------------------------------------------
    @extensionmethod
    def Resolve(self) -> "Type":
        return self

    # ----------------------------------------------------------------------
    @property
    @extensionmethod
    def display_name(self) -> str:
        return self.NAME

    # ----------------------------------------------------------------------
    def Clone(
        self,
        *,
        range: Union[DoesNotExist, Range]=DoesNotExist.instance,  # pylint: disable=redefined-builtin
        cardinality: Union[DoesNotExist, Cardinality]=DoesNotExist.instance,
        metadata: Union[DoesNotExist, None, Metadata]=DoesNotExist.instance,
    ) -> "Type":
        return self.Resolve()._CloneImpl(  # pylint: disable=protected-access
            self.range if isinstance(range, DoesNotExist) else range,
            self.cardinality if isinstance(cardinality, DoesNotExist) else cardinality,
            self.metadata if isinstance(metadata, DoesNotExist) else metadata,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "cardinality", self.cardinality

        if self.metadata:
            yield "metadata", self.metadata

    # ----------------------------------------------------------------------
    @abstractmethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "Type":
        raise Exception("Abstract method")  # pragma: no cover
