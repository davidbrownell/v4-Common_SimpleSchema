# ----------------------------------------------------------------------
# |
# |  GuidType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:39:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GuidType object"""

from dataclasses import dataclass
from typing import ClassVar, Tuple, Type as PythonType
from uuid import UUID

from ..FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class GuidType(FundamentalType):
    """A guid"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Guid"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (UUID, )
