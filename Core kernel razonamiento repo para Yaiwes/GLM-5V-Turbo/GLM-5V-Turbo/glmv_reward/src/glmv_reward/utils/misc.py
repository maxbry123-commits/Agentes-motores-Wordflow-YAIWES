# -*- coding: utf-8 -*-


from collections.abc import Sequence
from typing import TypeVar, Union, cast

T = TypeVar("T")


def ensure_list(obj: Union[Sequence[T], T]) -> list[T]:
    # `str`/`bytes` are `Sequence` subclasses, but callers hand them over as a
    # single scalar value (a prompt, an API key, a judge URL) rather than as a
    # sequence of characters. Wrap them like any other non-sequence value so we
    # don't explode "sk-abc" into ["s", "k", "-", "a", "b", "c"].
    if isinstance(obj, (str, bytes, bytearray)):
        return [cast(T, obj)]
    if isinstance(obj, Sequence):
        return list(obj)
    return [obj]


def ensure_text(text: Union[str, bytes], encoding: str = "utf-8") -> str:
    if isinstance(text, bytes):
        return text.decode(encoding)
    return text
