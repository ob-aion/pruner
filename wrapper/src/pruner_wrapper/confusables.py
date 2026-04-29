"""Cyrillic / Greek confusables for the PI-UNI-004 instruction-token homoglyph check.

Discrete-signal layer; Cisco's pass-7 covers the broader TR39 corpus. The 12
target instruction tokens are listed in `rules/unicode-tags/PI-UNI-004-*.yml`.
"""

from __future__ import annotations

# Map ASCII letter -> set of confusable codepoints.
# Conservative subset of Unicode TR39 confusables — covers Cyrillic + Greek
# substitutions for the instruction tokens the PI-UNI-004 rule targets.
ASCII_TO_CONFUSABLES: dict[str, frozenset[str]] = {
    "a": frozenset({"а", "ɑ", "α"}),  # Cyrillic а, Latin ɑ, Greek α
    "b": frozenset({"в", "б"}),  # Cyrillic в, б
    "c": frozenset({"с", "ϲ", "С"}),  # Cyrillic с, Greek ϲ
    "d": frozenset({"ԁ"}),
    "e": frozenset({"е", "ε", "ҽ"}),  # Cyrillic е, Greek ε
    "f": frozenset({"ϝ", "ḟ"}),  # Greek digamma, Latin f with dot
    "g": frozenset({"ɡ", "ց"}),
    "h": frozenset({"һ", "հ"}),
    "i": frozenset({"і", "ι", "ɩ"}),  # Cyrillic і, Greek ι
    "j": frozenset({"ј"}),
    "k": frozenset({"к", "κ"}),  # Cyrillic к, Greek κ
    "l": frozenset({"ӏ", "ⅼ"}),
    "m": frozenset({"м", "μ"}),  # Cyrillic м, Greek μ
    "n": frozenset({"η", "ո"}),
    "o": frozenset({"о", "ο", "o"}),  # Cyrillic о, Greek ο
    "p": frozenset({"р", "ρ"}),  # Cyrillic р, Greek ρ
    "q": frozenset({"ԛ"}),
    "r": frozenset({"г", "ɼ"}),
    "s": frozenset({"ѕ"}),  # Cyrillic ѕ
    "t": frozenset({"τ", "т"}),  # Greek τ, Cyrillic т
    "u": frozenset({"υ", "ս"}),  # Greek υ
    "v": frozenset({"ν"}),  # Greek ν
    "w": frozenset({"ѡ", "ԝ"}),
    "x": frozenset({"х", "χ"}),  # Cyrillic х, Greek χ
    "y": frozenset({"у", "ʏ"}),  # Cyrillic у
    "z": frozenset({"ʐ"}),
}


def confusables_for(char: str) -> frozenset[str]:
    """Return the confusables set for a single ASCII char (lower-case)."""

    return ASCII_TO_CONFUSABLES.get(char.lower(), frozenset())


def has_any_homoglyph(token: str, target_ascii: str) -> bool:
    """Return True if `token` is a same-length lookalike of `target_ascii`.

    Each character in `token` must either equal the corresponding ASCII
    character or be a confusable for it, and AT LEAST ONE character must be
    a non-ASCII confusable. The token must be the same length as the target.
    """

    if len(token) != len(target_ascii):
        return False

    has_non_ascii = False
    for ch, target_ch in zip(token, target_ascii.lower(), strict=True):
        if ch == target_ch:
            continue
        if ch in confusables_for(target_ch):
            has_non_ascii = True
            continue
        return False
    return has_non_ascii
