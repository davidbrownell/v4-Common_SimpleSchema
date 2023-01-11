# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
#
# The file has been automatically generated via ../Build.py using content
# in ../SimpleSchema.
#
# DO NOT MODIFY the contents of this file, as those changes will be
# overwritten the next time ../Build.py is invoked.
#
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring

from dataclasses import dataclass, field
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DirectoryType(FundamentalType):
    # ----------------------------------------------------------------------
    NAME = "Directory"

    # ----------------------------------------------------------------------
    ensure_exists: bool = field(default=True)
