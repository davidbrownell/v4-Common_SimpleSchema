# ----------------------------------------------------------------------
# |
# |  UriType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-25 22:52:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UriType object"""

import re

from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, Optional, Pattern, Tuple, Type as PythonType, Union

from Common_Foundation.Types import overridemethod

from ..FundamentalType import FundamentalType

from .....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Uri(object):
    """A uri broken down into its base components"""

    # ----------------------------------------------------------------------
    # |  Public Types
    @dataclass(frozen=True)
    class Authority(object):
        """The Authority component of a uri"""

        # ----------------------------------------------------------------------
        slashes: str
        username: Optional[str]
        host: str
        port: Optional[int]

        # ----------------------------------------------------------------------
        def __str__(self) -> str:
            return self._string

        # ----------------------------------------------------------------------
        @cached_property
        def _string(self) -> str:
            parts: list[str] = [self.slashes, ]

            if self.username:
                parts += [self.username, "@"]

            parts.append(self.host)

            if self.port:
                parts += [":", str(self.port)]

            parts.append("/")

            return "".join(parts)

    # ----------------------------------------------------------------------
    # |  Public Data
    scheme: str
    authority: Optional[Authority]
    path: Optional[str]
    query: Optional[str]
    fragment: Optional[str]

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __str__(self) -> str:
        return self._string

    # ----------------------------------------------------------------------
    # |  Private Properties
    @cached_property
    def _string(self) -> str:
        parts: list[str] = [self.scheme, ":"]

        if self.authority:
            parts.append(str(self.authority))

        if self.path:
            parts.append(self.path)

        if self.query:
            parts += ["?", self.query]

        if self.fragment:
            parts += ["#", self.fragment]

        return "".join(parts)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UriType(FundamentalType):
    """A uri"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Uri"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (str, Uri, )

    _VALIDATION_EXPRESSION: ClassVar[Pattern]                               = re.compile(
        r"""(?#
            Start of String                 )^(?#
            Scheme                          )(?P<scheme>[a-z]+):(?#
            Authority Begin                 )(?:(?#
                Slashes                     )(?P<slashes>///?)(?#
                User Info Begin             )(?:(?#
                    Username                )(?P<username>[^@/]+?)(?#
                    @                       )@(?#
                User Info End               ))?(?#
                Host                        )(?P<host>[^:/]+?)(?#
                Port Begin                  )(?:(?#
                    :                       ):(?#
                    Port                    )(?P<port>\d+)(?#
                Port End                    ))?(?#
            Authority End                   ))?(?#
            Path Begin                      )(?:(?#
                Slash                       )/(?#
                Path                        )(?P<path>[^:?\#]*?)(?#
            Path End                        ))?(?#
            Query Begin                     )(?:(?#
                ?                           )\?(?#
                Query                       )(?P<query>[^#]+?)(?#
            Query End                       ))?(?#
            Fragment Begin                  )(?:(?#
                #                           )\#(?#
                Fragment                    )(?P<fragment>.+?)(?#
            Fragment End                    ))?(?#
            End of String                   )$(?#
        )""",
    )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: Union[str, Uri],
    ) -> Uri:
        if isinstance(value, Uri):
            return value

        match = self.__class__._VALIDATION_EXPRESSION.match(value)  # pylint: disable=protected-access

        if not match:
            raise Exception(Errors.uri_type_invalid_value.format(value=value))

        authority: Optional[Uri.Authority] = None

        if match.group("slashes"):
            port = match.group("port")

            if port:
                port = int(port)
            else:
                port = None

            authority = Uri.Authority(
                match.group("slashes"),
                match.group("username") or None,
                match.group("host"),
                port,
            )

        return Uri(
            match.group("scheme"),
            authority,
            match.group("path") or None,
            match.group("query") or None,
            match.group("fragment") or None,
        )
