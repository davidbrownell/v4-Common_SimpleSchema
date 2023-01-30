# ----------------------------------------------------------------------
# |
# |  FilenameType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:40:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FilenameType object"""

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
class FilenameType(FundamentalType):
    """A filename"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Filename"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (Path, )

    ensure_exists: bool                     = field(default=True, kw_only=True)
    match_any: bool                         = field(default=False, kw_only=True)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.match_any and not self.ensure_exists:
            raise ValueError("'match_any' should only be set when 'ensure_exists' is set as well.")

        super(FilenameType, self).__post_init__()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _display_name(self) -> str:
        result = super(FilenameType, self)._display_name

        if self.ensure_exists:
            result += "!"

        if self.match_any:
            result += "^"

        return result

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "FilenameType":
        return FilenameType(
            range_value,
            cardinality,
            metadata,
            ensure_exists=self.ensure_exists,
            match_any=self.match_any,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Path,
    ) -> Path:
        if self.ensure_exists:
            if self.match_any and not value.exists():
                raise Exception(Errors.filename_type_does_not_exist.format(value=value))
            elif not self.match_any and not value.is_file():
                raise Exception(Errors.filename_type_invalid_file.format(value=value))

        return value
