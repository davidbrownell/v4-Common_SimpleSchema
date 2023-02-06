# ----------------------------------------------------------------------
# |
# |  DurationType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:38:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DurationType object"""

from dataclasses import dataclass
from datetime import timedelta
from typing import ClassVar, Tuple, Type as PythonType

from ..FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DurationType(FundamentalType):
    """A duration"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Duration"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (timedelta, )
