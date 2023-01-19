# ----------------------------------------------------------------------
# |
# |  Directory.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:41:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DirectoryConstraint and DirectoryType objects"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Type as TypeOf

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType
from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.Boolean import BooleanConstraint


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DirectoryConstraint(Constraint):
    """Ensure that a value is a directory value"""

    ensure_exists: bool                                 = field(kw_only=True, default=True)

    _expected_python_types: Tuple[TypeOf, ...]           = field(init=False, default_factory=lambda: (Path, ))

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(DirectoryConstraint, self).__post_init__()

        BooleanConstraint.Create()(self.ensure_exists)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ValidateImpl(
        self,
        value: Path,
    ) -> Path:
        if self.ensure_exists and not value.is_dir():
            raise Exception("'{}' is not a valid directory.".format(value))

        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DirectoryType(FundamentalType):
    """A directory"""

    # ----------------------------------------------------------------------
    NAME                                    = "Directory"
    CONSTRAINT_TYPE                         = DirectoryConstraint
    EXPRESSION_TYPES                        = None
