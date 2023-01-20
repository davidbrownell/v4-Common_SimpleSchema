# ----------------------------------------------------------------------
# |
# |  SimpleElement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 07:38:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SimpleElement object"""

from dataclasses import dataclass
from typing import Generic, TypeVar

from .Element import Element


# ----------------------------------------------------------------------
SimpleElementType                           = TypeVar("SimpleElementType")  # pylint: disable=invalid-name


@dataclass(frozen=True)
class SimpleElement(Generic[SimpleElementType], Element):
    """Element with a single value member"""

    # ----------------------------------------------------------------------
    value: SimpleElementType
