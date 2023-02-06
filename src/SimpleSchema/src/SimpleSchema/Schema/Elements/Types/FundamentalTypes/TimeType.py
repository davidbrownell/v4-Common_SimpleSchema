# ----------------------------------------------------------------------
# |
# |  TimeType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 13:57:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TimeType object"""

from dataclasses import dataclass
from datetime import time
from typing import ClassVar, Tuple, Type as PythonType

from ..FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TimeType(FundamentalType):
    """A time"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Time"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (time, )
