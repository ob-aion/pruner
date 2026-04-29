"""SPDX identifier list used by FC005 (license SPDX validation)."""

from __future__ import annotations

# Top OSI-approved identifiers covering the bulk of OSS skill repositories.
# Expansion procedure documented in `docs/writing-rules.md`.
SPDX_IDENTIFIERS: frozenset[str] = frozenset(
    {
        "0BSD",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "Apache-1.1",
        "Apache-2.0",
        "Artistic-2.0",
        "BSD-2-Clause",
        "BSD-2-Clause-Patent",
        "BSD-3-Clause",
        "BSD-3-Clause-Clear",
        "BSL-1.0",
        "CC0-1.0",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "CDDL-1.0",
        "CDDL-1.1",
        "EPL-1.0",
        "EPL-2.0",
        "EUPL-1.2",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "ISC",
        "LGPL-2.1-only",
        "LGPL-2.1-or-later",
        "LGPL-3.0-only",
        "LGPL-3.0-or-later",
        "MIT",
        "MIT-0",
        "MPL-2.0",
        "OFL-1.1",
        "Unlicense",
        "WTFPL",
        "Zlib",
    }
)


def is_valid_spdx(identifier: str) -> bool:
    """Return True if `identifier` is a recognised SPDX expression."""

    return identifier in SPDX_IDENTIFIERS
