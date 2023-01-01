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
from dataclasses import dataclass, field
from typing import Optional
from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FilenameType(Type):
    exists: Optional[bool] = field(default=True)
    match_any: Optional[bool] = field(default=False)
