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
    "Sentinel",
    "SentinelOr",
)

import sys
import typing
import threading

import typing_extensions

_sinstances = {}
_lock = threading.Lock()

_SelfT = typing.TypeVar("_SelfT")


class Sentinel:
    __slots__: typing.Sequence[str] = (
        "_name",
        "_repr",
        "_module",
    )

    def __new__(
        cls,
        name: str,
        module: typing.Optional[str] = None,
        repr: typing.Optional[str] = None,
    ) -> Sentinel:
        if module is None:
            # https://github.com/python/cpython/blob/
            # 67444902a0f10419a557d0a2d3b8675c31b075a9/
            # Lib/collections/__init__.py#L503
            try:
                module = sys._getframe(1).f_globals.get("__name__", "__main__")
            except (AttributeError, ValueError):
                module = __name__

        if repr is None:
            repr = f"<{name.split('.')[-1]}>"

        key = sys.intern(
            f"{cls.__module__}-{cls.__qualname__}-{module}-{name}"
        )
        try:
            return _sinstances[key]
        except KeyError:
            sentinel = super().__new__(cls)
            sentinel._name = name
            sentinel._repr = repr
            sentinel._module = module

            with _lock:
                return _sinstances.setdefault(key, sentinel)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._repr

    def __reduce__(self: _SelfT) -> typing.Tuple[
        typing.Type[_SelfT], typing.Tuple[str, str, str],
    ]:
        reduce = (
            self.__class__,
            (
                self._name,
                self._module,
                self._repr,
            ),
        )
        return reduce

    def __copy__(self) -> typing_extensions.Self:
        return self

    def __deepcopy__(
        self, memo: typing.MutableMapping[int, typing.Any]
    ) -> typing_extensions.Self:
        memo[id(self)] = self
        return self


_T = typing.TypeVar("_T")
SentinelOr = typing.Union[_T, Sentinel]
