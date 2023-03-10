# ----------------------------------------------------------------------
# |
# |  ReferenceCountMixin.py
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
"""Contains the ReferenceCountMixin object"""

import threading

from dataclasses import dataclass, field
from typing import Union

from Common_Foundation.Types import extensionmethod


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ReferenceCountMixin(object):
    """Mixin that supports referencing counting an Element"""

    # ----------------------------------------------------------------------
    _unique_type_name: Union[
        None,                               # Before NormalizeUniqueTypeName is called
        str,                                # After NormalizeUniqueTypeName is called
    ]                                       = field(init=False, default=None)

    _reference_count: int                   = field(init=False, default=0)
    _reference_count_lock: threading.Lock   = field(init=False, default_factory=threading.Lock)

    # ----------------------------------------------------------------------
    @property
    def is_unique_type_name_normalized(self) -> bool:
        return self._unique_type_name is not None

    @property
    def unique_type_name(self) -> str:
        # Valid after NormalizeUniqueTypeName is called
        assert self._unique_type_name
        return self._unique_type_name

    @property
    def reference_count(self) -> int:
        # Not acquiring the lock here, as we are assuming that this will only be invoked
        # after the reference count increment process is complete.
        return self._reference_count

    # ----------------------------------------------------------------------
    @extensionmethod
    def Increment(
        self,
        *,
        shallow: bool=False,  # pylint: disable=unused-argument
    ) -> None:
        with self._reference_count_lock:
            # Hack that allows the reference count to be modified even though the object
            # is frozen.
            object.__setattr__(
                self,
                "_reference_count",
                self._reference_count + 1,
            )

    # ----------------------------------------------------------------------
    def NormalizeUniqueTypeName(
        self,
        unique_type_name: str,
    ) -> None:
        assert self._unique_type_name is None
        object.__setattr__(self, "_unique_type_name", unique_type_name)
