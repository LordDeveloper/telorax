from __future__ import annotations


def parse_version(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in value.strip().lstrip('v').split('.'):
        digits = ''.join(char for char in piece if char.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def version_lt(left: str, right: str) -> bool:
    return parse_version(left) < parse_version(right)
