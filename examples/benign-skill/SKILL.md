---
name: "code-formatter"
description: "Formats Python files with black and isort."
allowed-tools: Read,Edit
license: "Apache-2.0"
metadata:
  author: coroboros
---

# Code formatter

A narrow utility skill. Formats Python files in place using `black` and `isort`.

## When to use

When the user asks to format Python code or normalise import order.

## How

```bash
black <path> && isort <path>
```

The skill expects `black` and `isort` to be installed in the environment. It does not write to identity files, does not fetch external URLs, does not embed inline-deps without pins, and does not contain hidden Unicode payloads.
