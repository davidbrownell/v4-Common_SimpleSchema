# ----------------------------------------------------------------------
# |
# |  Filename.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 13:55:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FilenameConstraint and FilenameType objects"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Type as TypeOf

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Types.FundamentalType import Constraint, FundamentalType
from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.Boolean import BooleanConstraint


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FilenameConstraint(Constraint):
    """Ensure that a value is a filename value"""

    ensure_exists: bool                                 = field(kw_only=True, default=True)
    match_any: bool                                     = field(kw_only=True, default=False)

    _expected_python_types: Tuple[TypeOf, ...]          = field(init=False, default_factory=lambda: (Path, ))

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(FilenameConstraint, self).__post_init__()

        bool_constraint = BooleanConstraint.Create()

        bool_constraint(self.ensure_exists)
        bool_constraint(self.match_any)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ValidateImpl(
        self,
        value: Path,
    ) -> Path:
        if self.ensure_exists:
            if self.match_any and not value.exists():
                raise Exception("'{}' is not a valid filename or directory.".format(value))

            if not self.match_any and not value.is_file():
                raise Exception("'{}' is not a valid filename.".format(value))

        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FilenameType(FundamentalType):
    """A filename"""

    # ----------------------------------------------------------------------
    NAME                                    = "Filename"
    CONSTRAINT_TYPE                         = FilenameConstraint
    EXPRESSION_TYPES                        = None
