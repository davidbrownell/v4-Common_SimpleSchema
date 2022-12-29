# ----------------------------------------------------------------------
# |
# |  ParseType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-28 16:41:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseType object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseType(Type):
    """Temporary type generated during Parsing and replaced during subsequent steps"""

    pass
