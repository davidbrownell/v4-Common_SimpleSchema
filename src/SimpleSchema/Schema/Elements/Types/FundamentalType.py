# ----------------------------------------------------------------------
# |
# |  FundamentalType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-09 15:12:20
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

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FundamentalType(Type):
    """Abstract base class for fundamental types"""

    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def display_name(self) -> str:
        return self.NAME

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateAcceptReferenceDetails(self) -> Element:
        return self

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        raise Exception("This should never be called on FundamentalType instances.")
