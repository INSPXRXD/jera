# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2024 INSPXRXD
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from __future__ import annotations

__all__: typing.Sequence[str] = (
    "__author__",
    "__maintainer__",
    "__copyright__",
    "__email__",
    "__license__",
    "__version__",
    "version",
)

import re
import typing

__author__: typing.Final[str] = "INSPXRXD"
__maintainer__: typing.Final[str] = "INSPXRXD"
__copyright__: typing.Final[str] = "2024-present, INSPXRXD"
__email__: typing.Final[str] = "inspxrxd@gmail.com"
__license__: typing.Final[str] = "MIT"
__version__: typing.Final[str] = "0.0a0"

_indev_pattern: typing.Pattern[str] = re.compile(
    (
        r"^(?P<major>\d+)"
        r"\."
        r"(?P<minor>\d+)"
        r"(?P<stage>a|b|rc)"
        r"(?P<serial>\d+)$"
    ),
    re.MULTILINE | re.VERBOSE,
)
_final_pattern: typing.Pattern[str] = re.compile(
    (
        r"^(?P<major>\d+)"
        r"\."
        r"(?P<minor>\d+)"
    ),
    re.MULTILINE | re.VERBOSE,
)


class Version(typing.NamedTuple):
    major: int
    minor: int
    serial: int
    stage: typing.Optional[typing.Literal["a", "b", "rc"]] = None
    """https://peps.python.org/pep-0440/
    
    Note that the development stage is set to None if the project is 
    already completed and in its final state.
    """

    @classmethod
    def final(cls, major: int, minor: int) -> Version:
        self = cls(
            major=int(major),
            minor=int(minor),
            stage=None,
            serial=0,
        )
        return self

    @classmethod
    def from_str(cls, version_str: str) -> Version:
        match = re.match(_indev_pattern, version_str)
        if match is not None:
            major, minor, stage, serial = match.groups()
            self = Version(
                major=int(major),
                minor=int(minor),
                stage=stage,
                serial=int(serial),
            )
            return self

        final_match = re.match(_final_pattern, version_str)
        if (
            final_match is None
            or any(c.isalpha() for c in version_str)
            # For example, 3.3a. A final version cannot have
            # a development stage.
            or len(version_str.split(".")) > 2
            # For example, 3.3.3.A final version cannot have
            # a serial number for the current development
            # stage, as it is final.
        ):
            raise ValueError(
                f"Invalid version string: {version_str}"
            )

        return cls.final(*final_match.groups())

    def is_final(self) -> bool:
        return self.stage is None


version = Version.from_str(__version__)
"""Current version of the project. 

major : int
-----
Indicates a major release of the software, usually involving 
significant changes or new features. 

Note that changes in the major version may be incompatible 
with previous versions. 

minor : int
-----
Indicates a less significant release, usually including minor 
improvements or new features that are compatible with previous 
versions.

serial : int
------
Used to indicate the sequential release number within a current 
development stage. 

stage : Optional[Literal["a", "b", "rc"]], default None
-----
Indicates the development stage of the software version. 

Three stages are used:
    * a (alpha): Early development stage, where the software may 
    be unstable. Core features may be implemented 
    but not fully tested.
                 
    * b (beta): The next development stage, where the software is 
    more stable but may still contain bugs.
    
    * rc (release candidate): A preliminary release that could 
    potentially become the final version if no critical issues are 
    found.
"""
