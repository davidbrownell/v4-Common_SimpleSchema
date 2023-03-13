# ----------------------------------------------------------------------
# |
# |  UniqueNameTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-22 15:12:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UniqueNameTrait object"""

from dataclasses import dataclass, field
from typing import Union


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UniqueNameTrait(object):
    """Trait for Elements that are given a unique name during Parsing"""

    # ----------------------------------------------------------------------
    _unique_name: Union[
        None,                               # Before NormalizeUniqueName is called
        str,                                # After NormalizeUniqueName is called
    ]                                       = field(init=False, default=None)

    # ----------------------------------------------------------------------
    @property
    def is_unique_name_normalized(self) -> bool:
        return self._unique_name is not None

    @property
    def unique_name(self) -> str:
        # Valid after NormalizeUniqueName is called
        assert self._unique_name
        return self._unique_name

    # ----------------------------------------------------------------------
    def NormalizeUniqueName(
        self,
        unique_name: str,
    ) -> None:
        assert self._unique_name is None
        object.__setattr__(self, "_unique_name", unique_name)
