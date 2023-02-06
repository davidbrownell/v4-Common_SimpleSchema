# ----------------------------------------------------------------------
# |
# |  DateType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:30:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DateType object"""

from dataclasses import dataclass
from datetime import date
from typing import ClassVar, Tuple, Type as PythonType

from ..FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DateType(FundamentalType):
    """A date"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Date"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (date, )
