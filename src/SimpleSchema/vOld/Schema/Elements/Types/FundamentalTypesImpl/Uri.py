# ----------------------------------------------------------------------
# |
# |  Uri.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:20:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UriConstraint and UriType objects"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Types.FundamentalTypesImpl.String import StringConstraint


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UriConstraint(StringConstraint):
    """Ensure that a value is a uri value"""

    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UriType(FundamentalType):
    """A uri"""

    # ----------------------------------------------------------------------
    NAME                                    = "Uri"
    CONSTRAINT_TYPE                         = UriConstraint
    EXPRESSION_TYPES                        = None
