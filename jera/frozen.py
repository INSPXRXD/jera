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

__all__: typing.Sequcence[str] = ("FrozenMeta",)

import abc
import typing
import sys

FROZEN: typing.Final[str] = "__frozen__"
UNFREEZE_ATTRS: typing.Final[str] = "__unfreeze_attrs__"
UNFREEZE_ATTRS_DEFAULT_SET: typing.Final[typing.AbstractSet[str]] = {
    "__frozen_setattr__",
    "__frozen_delattr__",
    "__init__",
}


def __frozen_setattr__(
    self: typing.Any,
    key: typing.Any,
    value: typing.Any,
) -> None:
    if (
        self.__frozen__
        and sys._getframe().f_back.f_code.co_name not in self.__unfreeze_attrs__
    ):
        raise FrozenInstanceError(f"{self!r} instance is frozen.")

    if hasattr(self, "__dict__"):
        self.__dict__[key] = value
        return

    object.__setattr__(self, key, value)


def __frozen_delattr__(self: typing.Any, item: typing.Any) -> None:
    if (
        self.__frozen__
        and sys._getframe().f_back.f_code.co_name not in self.__unfreeze_attrs__
    ):
        raise FrozenInstanceError(f"{self!r} instance is frozen.")

    object.__delattr__(self, item)


class FrozenInstanceError(Exception):
    pass


class FrozenMeta(abc.ABCMeta):
    """
    A class that freezes the methods `__setattr__`, `__setitem__`,
    `__delattr__`, and `__delitem__` for the current instance of the
    class. However, the class can be modified in `__init__` for
    initial initialization.

    Note that the class inherits from `abc.ABCMeta` to allow
    subclasses to inherit all the functionality of `abc.ABC` for
    implementing interfaces or abstractions.

    __frozen__ : bool
    ----------
    A flag to determine the state of the current instance, whether
    it is frozen or not. By default, it is set to builtins.True.

    __unfreeze_attrs__ : set
    ------------------
    A parameter that defines the attributes that will be unfrozen
    and therefore can change the state of the current instance of
    the class.

    This parameter is implicit and can create many unexpected problems,
    so use it with caution and only in very exotic cases.
    """

    def __new__(
        mcs: typing.Type[FrozenMeta],
        name: str,
        bases: typing.Tuple[typing.Type[typing.Any], ...],
        attrs: typing.Dict[str, typing.Any],
    ) -> typing.Any:
        frozen = attrs.pop(FROZEN, True)
        if not isinstance(frozen, bool):
            raise ValueError(
                f"__frozen__ expected a boolean value, "
                f"but {type(frozen)}/{frozen} received."
            )

        unfreeze = attrs.pop(UNFREEZE_ATTRS, set())
        if not isinstance(unfreeze, set):
            raise ValueError(
                f"__unfreeze_attrs__ expected a set value, "
                f"but {type(unfreeze)}/{unfreeze} received."
            )

        unfreeze |= UNFREEZE_ATTRS_DEFAULT_SET

        attrs[UNFREEZE_ATTRS] = unfreeze
        attrs[FROZEN] = frozen

        attrs["__setattr__"] = attrs["__setitem__"] = __frozen_setattr__
        attrs["__delattr__"] = attrs["__delitem__"] = __frozen_delattr__
        return super().__new__(mcs, name, bases, attrs)
