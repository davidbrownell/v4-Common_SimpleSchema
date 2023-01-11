# ----------------------------------------------------------------------
# |
# |  Type.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:49:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Type object"""

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod, overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Element):
    """Abstract base class for types"""

    # ----------------------------------------------------------------------
    NAME = ""

    # ----------------------------------------------------------------------
    cardinality: Cardinality
    metadata: Optional[Metadata]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME

    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def display_name(self) -> str:
        raise Exception("Abstract property")

    # ----------------------------------------------------------------------
    def Clone(
        self,
        *,
        range: Union[DoesNotExist, Range]=DoesNotExist.instance,  # pylint: disable=redefined-builtin
        cardinality: Union[DoesNotExist, Cardinality]=DoesNotExist.instance,
        metadata: Union[DoesNotExist, None, Metadata]=DoesNotExist.instance,
    ) -> "Type":
        with self.Resolve() as resolved_type:
            return resolved_type._CloneImpl(  # pylint: disable=protected-access
                self.range if isinstance(range, DoesNotExist) else range,
                self.cardinality if isinstance(cardinality, DoesNotExist) else cardinality,
                self.metadata if isinstance(metadata, DoesNotExist) else metadata,
            )

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def Resolve(self) -> Iterator["Type"]:
        yield self

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
