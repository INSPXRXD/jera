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

import copy
import pickle
import typing

import pytest

from jera import sentinel

sent1 = sentinel.Sentinel("sent1")
sent2 = sentinel.Sentinel("sent2", repr="test_sentinel.sent2")


@pytest.fixture(name="sentinel_defined_in_function")
def _() -> sentinel.Sentinel:
    sent = sentinel.Sentinel("sentinel_defined_in_function")
    return sent


class TestSentinel:
    def test_repr(self) -> None:
        assert repr(sent1) == "<sent1>"
        assert repr(sent2) == "test_sentinel.sent2"

    def test_type(self) -> None:
        assert isinstance(sent1, sentinel.Sentinel)
        assert isinstance(sent2, sentinel.Sentinel)

    def test_copy(self) -> None:
        assert sent1 is copy.copy(sent1)
        assert sent1 is copy.deepcopy(sent1)

    def test_same_object_in_same_module(self) -> None:
        copy1 = sentinel.Sentinel("sent1")
        assert copy1 is sent1

        copy2 = sentinel.Sentinel("sent1")
        assert copy2 is copy1

    def test_same_object_fake_module(self) -> None:
        copy1 = sentinel.Sentinel("Bar", module="u.n.d.e.f.i.n.e.d")
        copy2 = sentinel.Sentinel("Bar", module="u.n.d.e.f.i.n.e.d")
        assert copy1 is copy2

    def test_identity_in_different_modules(self) -> None:
        other_module_sent1 = sentinel.Sentinel("sent1", module="u.n.d.e.f.i.n.e.d")
        assert other_module_sent1 is not sent1

    def test_identity(self, sentinel_defined_in_function: sentinel.Sentinel) -> None:
        for sent in sent1, sent2, sentinel_defined_in_function:
            assert sent is sent
            assert sent == sent

    def test_pickle(self) -> None:
        assert sent1 is pickle.loads(pickle.dumps(sent1))

    def test_bool(self) -> None:
        assert sent1
        assert sentinel.Sentinel(":(")

    def test_auto_module_name(
        self, sentinel_defined_in_function: sentinel.Sentinel,
    ) -> None:
        assert sentinel.Sentinel("sent1", module=__name__) is sent1
        assert (
            sentinel.Sentinel("sentinel_defined_in_function", module=__name__)
            is sentinel_defined_in_function
        )

    def test_subclass(self) -> None:
        class AlwaysFalseSentinel(sentinel.Sentinel):
            def __bool__(self) -> typing.Literal[False]:
                return False

        sent = AlwaysFalseSentinel(":(")
        assert sent is sent
        assert sent == sent
        assert not sent

        non_subclass_sent = sentinel.Sentinel(":(")
        assert sent is not non_subclass_sent
        assert sent != non_subclass_sent

    def test_uniqueness(self) -> None:
        assert sent1 is not sent2
        assert sent1 != sent2
        assert sent1 is not None
        assert sent1 != None
        assert sent1 is not Ellipsis
        assert sent1 != Ellipsis
        assert sent1 is not "sent1"
        assert sent1 != "sent1"
        assert sent1 is not "<sent1>"
        assert sent1 != "<sent1>"
