# ----------------------------------------------------------------------
# |
# |  DateTimeType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:33:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DateTimeType object"""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Tuple, Type as PythonType

from ..FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DateTimeType(FundamentalType):
    """A datetime"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "DateTime"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (datetime, )
