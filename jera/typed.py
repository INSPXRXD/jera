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
    "Typed",
    "Attribute",
    "TYPED_CLASS_ATTRS",
    "TypedError",
    "MissingTypedAttribute",
)

import typing

from jera import undefined
from jera import errors

TYPED_CLASS_ATTRS: typing.Final[str] = "__typed_class_attrs__"

_SelfT = typing.TypeVar("_SelfT")


class TypedError(errors.JeraError):
    pass


class MissingTypedAttribute(TypedError):
    pass


class Attribute:
    __slots__: typing.Sequence[str] = ("compare", "hash",)

    def __init__(
        self,
        *,
        hash: typing.Optional[bool] = None,
        compare: typing.Optional[bool] = None,
    ) -> None:
        self.compare = compare
        self.hash = hash

    def is_comparable(self) -> bool:
        if self.hash is None:
            return self.compare
        return self.hash


class Typed:
    def __new__(
        cls: typing.Type[_SelfT],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> _SelfT:
        attrs = {}
        for k, v in typing.get_type_hints(cls.__init__).items():
            try:
                attrs[k] = v.__metadata__[0]
            except AttributeError:
                continue

        setattr(cls, TYPED_CLASS_ATTRS, attrs)
        self = super().__new__(cls)
        return self

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, Typed):
            return NotImplemented

        attrs = getattr(self, TYPED_CLASS_ATTRS, None)
        if attrs is None:
            return super().__eq__(other)

        count = len(attrs)
        for k, v in attrs.items():
            if not v.is_comparable():
                count -= 1
                if not count:
                    return False
                continue

            other_v = getattr(other, k, undefined.UNDEFINED)
            if other_v is undefined.UNDEFINED:
                # TODO: return False ?
                raise MissingTypedAttribute(
                    f"The attribute {k!r} is declared as a "
                    f"parameter in __init__, but is missing "
                    f"in the {type(self)!r} instance."
                )

            elif other_v != getattr(self, k):
                return False

        return True

    def __hash__(self) -> int:
        attrs = getattr(self, TYPED_CLASS_ATTRS, None)
        if not attrs:
            return super().__hash__()

        attrs = [
            k for k, v in attrs.items()
            if v.is_comparable()
        ]
        if not attrs:
            return NotImplemented

        value = hash(
            tuple(
                getattr(self, k)
                for k in attrs
            )
        )
        return value
