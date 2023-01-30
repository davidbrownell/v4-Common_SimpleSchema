# ----------------------------------------------------------------------
# |
# |  FundamentalType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 14:11:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FundamentalType object"""

from dataclasses import dataclass
from typing import Any

from Common_Foundation.Types import overridemethod

from .Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FundamentalType(Type):
    """Abstract base class for fundamental types"""

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        # Most fundamental types don't have any custom conversion logic, so the
        # default is not not do anything.
        return value
