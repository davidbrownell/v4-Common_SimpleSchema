# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-03 12:18:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains references to all of the generated fundamental types; this code must be manually updated if new fundamental types are added"""

from .GeneratedCode.BooleanType import BooleanType
from .GeneratedCode.DateTimeType import DateTimeType
from .GeneratedCode.DateType import DateType
from .GeneratedCode.DirectoryType import DirectoryType
from .GeneratedCode.DurationType import DurationType
from .GeneratedCode.EnumType import EnumType
from .GeneratedCode.FilenameType import FilenameType
from .GeneratedCode.GuidType import GuidType
from .GeneratedCode.IntegerType import IntegerType
from .GeneratedCode.NumberType import NumberType
from .GeneratedCode.StringType import StringType
from .GeneratedCode.TimeType import TimeType
from .GeneratedCode.UriType import UriType
