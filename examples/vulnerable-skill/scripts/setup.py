# /// script
# dependencies = ["requests", "rich"]
# ///

# Intentionally vulnerable: PEP-723 inline-deps without `==` pins (PI-PEP723-001 tripwire).

import requests  # noqa: F401  (vulnerability example)
