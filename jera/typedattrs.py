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
    "TypedAttrs",
    "Attribute",
    "TYPED_CLASS_ATTRS",
    "TypedAttrsError",
    "MissingTypedAttribute",
)

import functools
import typing

from jera import sentinel
from jera import errors
from jera import util

TYPED_CLASS_ATTRS: typing.Final[str] = "__typed_class_attrs__"

MissingValue = sentinel.Sentinel("MissingValue")
DefaultValue = sentinel.Sentinel("DefaultValue")

_SelfT = typing.TypeVar("_SelfT")


class TypedAttrsError(errors.JeraError):
    pass


class MissingTypedAttribute(TypedAttrsError):
    pass


class Attribute:
    __slots__: typing.Sequence[str] = (
        "compare",
        "hash",
        "default",
        "default_factory",
    )

    def __init__(
        self,
        *,
        hash: typing.Optional[bool] = None,
        compare: typing.Optional[bool] = None,
        default: sentinel.SentinelOr[
            typing.Any
        ] = MissingValue,
        default_factory: sentinel.SentinelOr[
            typing.Callable[[], typing.Any]
        ] = MissingValue,
    ) -> None:
        if (
            default is not MissingValue
            and default_factory is not MissingValue
        ):
            raise ValueError(
                "Cannot specify both default and default_factory"
            )

        if isinstance(default, (list, dict, set)):
            # FIXME: for attribute <name> ?
            raise ValueError(
                f"Mutable default {type(default)} for attribute "
                f"{self!r} is not allowed: use default_factory"
            )

        self.compare = compare
        self.hash = hash
        self.default = default
        self.default_factory = default_factory

    def __repr__(self) -> str:
        attributes = ", ".join(
            f"{k}={v}" for k, v in util.attributes(self)
        )
        return f"{self.__class__.__name__}({attributes})"

    def get_default(self) -> sentinel.SentinelOr[typing.Any]:
        if self.default_factory is not MissingValue:
            return self.default_factory()
        return self.default

    def is_comparable(self) -> bool:
        if self.hash is None:
            return self.compare
        return self.hash


class Attributes:
    def __init__(
        self,
        attributes: typing.Optional[
            typing.Mapping[str, Attribute]
        ] = None,
    ) -> None:
        self._attributes: typing.MutableMapping[
            str, Attribute
        ] = {}
        if attributes is not None:
            self._attributes.update(attributes)

    @property
    def comparable_attrs(self) -> typing.Mapping[str, Attribute]:
        comparable = {
            k: v for k, v
            in self._attributes.items()
            if v.is_comparable()
        }
        return comparable

    @property
    def all_attrs(self) -> typing.Mapping[str, Attribute]:
        return self._attributes


def replace_defaults_hook(__init__):
    @functools.wraps(__init__)
    def wrapper(self, *args, **kwargs):
        __init__(self, *args, **kwargs)

        try:
            attrs = getattr(
                self, TYPED_CLASS_ATTRS, MissingValue
            ).all_attrs
        except AttributeError:
            return

        for k, v in util.attributes(self):
            if v is DefaultValue:
                attr_default_v = attrs[k].get_default()
                if attr_default_v is MissingValue:
                    raise ValueError(
                        f"Expected attribute {k!r} to have "
                        f"a default value, but it is missing."
                    )

                setattr(self, k, attr_default_v)
                continue

    return wrapper


class TypedAttrs:
    def __new__(
        cls: typing.Type[_SelfT],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> _SelfT:
        attrs = {}

        any_has_default = False
        for k, v in typing.get_type_hints(cls.__init__).items():
            try:
                attr = attrs.setdefault(k, v.__metadata__[0])
            except AttributeError:
                continue

            if (
                attr.default is not MissingValue
                or attr.default_factory is not MissingValue
            ):
                any_has_default = True

        if any_has_default:
            cls.__init__ = replace_defaults_hook(cls.__init__)

        setattr(cls, TYPED_CLASS_ATTRS, Attributes(attrs))
        self = super().__new__(cls)
        return self

    def __eq__(self, other: typing.Any) -> bool:
        """
        By default, __ne__() delegates to __eq__() and inverts
        the result unless it is `NotImplemented`.
        """
        if other.__class__ is not self.__class__:
            return NotImplemented

        attrs: typing.Optional[Attributes] = getattr(
            self,
            TYPED_CLASS_ATTRS,
            None,
        )
        if attrs is None or not attrs.comparable_attrs:
            # If for some reason an attribute was removed from
            # the class or attributes for comparison are missing,
            # in such a case we will resort to comparing the
            # default states.
            return super().__eq__(other)

        for k in attrs.comparable_attrs:
            other_v: typing.Any = getattr(other, k, MissingValue)
            if other_v is MissingValue:
                # TODO: return False ?
                raise MissingTypedAttribute(
                    f"The attribute {k!r} is declared as a "
                    f"parameter in __init__(), but is missing "
                    f"in the {type(self)!r} instance."
                )

            elif other_v != getattr(self, k):
                return False

        return True

    def __hash__(self) -> int:
        attrs: typing.Optional[Attributes] = getattr(
            self,
            TYPED_CLASS_ATTRS,
            None,
        )
        if attrs is None or not attrs.comparable_attrs:
            # If for some reason an attribute was removed from
            # the class or attributes for comparison are missing,
            # in such a case we will resort to comparing the
            # default states.
            return super().__hash__()

        value = hash(
            tuple(
                getattr(self, k)
                for k in attrs.comparable_attrs
            )
        )
        return value
