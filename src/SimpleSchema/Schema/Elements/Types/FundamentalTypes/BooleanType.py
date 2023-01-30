# ----------------------------------------------------------------------
# |
# |  BooleanType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 16:47:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BooleanType object"""

from dataclasses import dataclass
from typing import ClassVar, Tuple, Type as PythonType

from Common_Foundation.Types import overridemethod

from ..FundamentalType import FundamentalType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BooleanType(FundamentalType):
    """A Boolean"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Boolean"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (bool, )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs) -> "BooleanType":
        return BooleanType(*args, **kwargs)
