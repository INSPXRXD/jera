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
    "UNDEFINED",
    "UndefinedOr",
)

import typing

import typing_extensions

_SelfT = typing.TypeVar("_SelfT")


def __new__(_: typing.Type[_SelfT]) -> _SelfT:
    raise TypeError(f"Cannot create multiple instances of NothingType.")


class UndefinedType:
    __slots__: typing.Sequence[str] = ()

    def __str__(self) -> str:
        return "NOTHING"

    def __repr__(self) -> str:
        return "<NOTHING>"

    def __reduce__(self) -> str:
        return "NOTHING"

    def __getstate__(self) -> typing.Any:
        return False

    def __bool__(self) -> typing.Literal[False]:
        return False

    def __copy__(self) -> typing_extensions.Self:
        return self

    def __deepcopy__(
        self, memo: typing.MutableMapping[int, typing.Any]
    ) -> typing_extensions.Self:
        memo[id(self)] = self
        return self


UNDEFINED = UndefinedType()
UndefinedType.__new__ = __new__
del __new__

_T = typing.TypeVar("_T")
UndefinedOr = typing.Union[_T, UndefinedType]
