# ----------------------------------------------------------------------
# |
# |  DirectoryType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:34:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DirectoryType object"""

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import ClassVar, Optional, Tuple, Type as PythonType

from Common_Foundation.Types import overridemethod

from ..FundamentalType import FundamentalType

from ...Common.Cardinality import Cardinality
from ...Common.Metadata import Metadata

from .....Common import Errors
from .....Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DirectoryType(FundamentalType):
    """A directory"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Directory"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (Path, )

    ensure_exists: bool                     = field(default=True, kw_only=True)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _display_name(self) -> str:
        result = super(DirectoryType, self)._display_name

        if self.ensure_exists:
            result += "!"

        return result

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "DirectoryType":
        return DirectoryType(range_value, cardinality, metadata, ensure_exists=self.ensure_exists)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Path,
    ) -> Path:
        if self.ensure_exists and not value.is_dir():
            raise Exception(Errors.directory_type_invalid_dir.format(value=value))

        return value
