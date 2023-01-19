# ----------------------------------------------------------------------
# |
# |  FundamentalTypes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 14:30:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Convenience imports for Fundamental types"""

# pylint: disable=unused-import
from .FundamentalTypesImpl.Boolean import BooleanConstraint, BooleanType
from .FundamentalTypesImpl.Date import DateConstraint, DateType
from .FundamentalTypesImpl.DateTime import DateTimeConstraint, DateTimeType
from .FundamentalTypesImpl.Directory import DirectoryConstraint, DirectoryType
from .FundamentalTypesImpl.Duration import DurationConstraint, DurationType
from .FundamentalTypesImpl.Enum import EnumConstraint, EnumType
from .FundamentalTypesImpl.Filename import FilenameConstraint, FilenameType
from .FundamentalTypesImpl.Guid import GuidConstraint, GuidType
from .FundamentalTypesImpl.Integer import IntegerConstraint, IntegerType
from .FundamentalTypesImpl.NoneType import NoneConstraint, NoneType
from .FundamentalTypesImpl.Number import NumberConstraint, NumberType
from .FundamentalTypesImpl.String import StringConstraint, StringType
from .FundamentalTypesImpl.Time import TimeConstraint, TimeType
from .FundamentalTypesImpl.Uri import UriConstraint, UriType
