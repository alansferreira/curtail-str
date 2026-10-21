"""Pure identifier abbreviation; see the shared algorithm specification."""

import re
import unicodedata
from collections.abc import Mapping
from typing import Literal, TypedDict


class Options(TypedDict, total=False):
    mode: Literal["universal", "custom", "configurable"]
    replacements: Mapping[str, str]
    min_word_length: int
    preserve_word_length: int
    max_word_length: int


_SEPARATORS = re.compile(
    r"[-_\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a"
    r"\u2028\u2029\u202f\u205f\u3000]+"
)
_LIMITS = {"min_word_length": 3, "preserve_word_length": 3, "max_word_length": 4}
_OPTIONS = frozenset(("mode", "replacements", *_LIMITS))


def _valid_string(value: object) -> None:
    if not isinstance(value, str) or any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise TypeError("Expected a well-formed Unicode string")


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFC", "".join(c.lower() for c in value))


def _compress(word: str, maximum: int) -> str:
    tail: list[str] = []
    removing = False
    for char in unicodedata.normalize("NFD", word[1:]):
        if char in "aeiou":
            removing = True
        elif not (removing and unicodedata.category(char).startswith("M")):
            tail.append(char)
            removing = False
    result: list[str] = []
    previous = None
    for char in word[0] + unicodedata.normalize("NFC", "".join(tail)):
        if char != previous or not unicodedata.category(char).startswith("L"):
            result.append(char)
        previous = char
    return "".join(result[:maximum])


def encurtar_chave_universal(value: str | None, options: Options | None = None) -> str:
    """Abbreviate a key, raising TypeError/ValueError for invalid arguments."""
    supplied = {} if options is None else options
    if not isinstance(supplied, Mapping):
        raise TypeError("Options must be a mapping")
    if any(key not in _OPTIONS for key in supplied):
        raise ValueError("Unknown option")
    mode = supplied.get("mode", "universal")
    if mode not in ("universal", "custom", "configurable"):
        raise ValueError("Unknown mode")
    if "replacements" in supplied and mode == "universal":
        raise ValueError("Replacements require custom or configurable mode")
    limits = {}
    for key, default in _LIMITS.items():
        if key in supplied and mode != "configurable":
            raise ValueError("Limits require configurable mode")
        limit = supplied.get(key, default)
        if type(limit) is not int or not 1 <= limit <= 2147483647:
            raise ValueError(f"{key} must be an integer between 1 and 2147483647")
        limits[key] = limit
    replacements: dict[str, str] = {}
    if "replacements" in supplied:
        mapping = supplied["replacements"]
        if not isinstance(mapping, Mapping):
            raise TypeError("Replacements must be a mapping")
        for key, replacement in mapping.items():
            _valid_string(key)
            _valid_string(replacement)
            normalized = _normalize(key)
            if not normalized or _SEPARATORS.search(normalized) or normalized in replacements:
                raise ValueError("Invalid or colliding replacement key")
            replacements[normalized] = replacement
    if value is None:
        return ""
    _valid_string(value)
    output: list[str] = []
    for word in _SEPARATORS.split(_normalize(value)):
        if not word:
            continue
        if word in replacements:
            result = replacements[word]
        elif len(word) < limits["min_word_length"]:
            continue
        elif len(word) <= limits["preserve_word_length"]:
            result = word
        else:
            result = _compress(word, limits["max_word_length"])
        if result:
            output.append(result)
    return "-".join(output)


__all__ = ["Options", "encurtar_chave_universal"]
