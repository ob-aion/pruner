# Coverage matrix

Honest three-column table: what `cisco-ai-skill-scanner` catches × what the Coroboros pack adds × what nothing covers at v0.1.0. Single source of truth for "what does Pruner detect."

| Threat class (OWASP AST + LLM ref) | Cisco catches | Coroboros pack adds | Nothing covers |
|---|---|---|---|
| Direct PI in body / frontmatter (LLM01 / AST01) | yes — multi-pass + LLM-judge meta + deterministic | — | latent semantic activation, post-N-invocation backdoors |
| Imperative override patterns (`ignore previous`, `you are now`) (LLM01 / AST01) | yes | — | — |
| Description-field weaponisation (AST04) | yes | FC001 (kebab-case + reserved-tokens) refines house posture | — |
| Hidden Unicode Tag block U+E0000–U+E007F (LLM01 / AST01) | yes (pass-7) | **PI-UNI-001** as discrete signal | — |
| Variation selectors carrying payload (FE00–FE0F, E0100–E01EF) | partial | **PI-UNI-002** with cluster threshold ≥ 4 | — |
| Bidi override / Trojan Source (CVE-2021-42574) | yes | **PI-UNI-003** as discrete signal | — |
| Cyrillic / Greek homoglyphs in instruction tokens | yes (pass-7) | **PI-UNI-004** for `ignore`, `system`, `prompt`, `instructions`, `override`, `disregard`, `forget`, `you`, `are`, `now`, `admin`, `root` | TR39 long-tail homoglyphs not in instruction-token set |
| Zero-width characters | yes | — | — |
| ANSI escape sequences | yes | — | — |
| Base64 / hex / rot13-encoded instructions | yes | — | — |
| HTML-comment-hidden instructions | yes | — | — |
| Indirect injection through `references/*.md`, `assets/*.md` | yes | — | — |
| Markdown-image data exfiltration (`![...](https://...?...=...)`) | partial | **PI-MDIMG-001** | — |
| Indirect injection via fetched URLs (RAG, web_fetch) | flag-only (no fetch) | flag-only (no fetch) | content of fetched URLs is out of scope |
| Image / PDF OCR injection | partial (Cisco's PDF + macro passes) | — | full multimodal pipeline |
| Tool/function abuse — `allowed-tools: Read` only but scripts call `Bash` | yes | — | — |
| Wildcard tool grants (`Bash(*)`, `Read(*)`) | yes | — | — |
| Description vs. body permission mismatch | yes | — | — |
| Identity-file writes (AGENTS.md, MEMORY.md, .bashrc, .cursorrules, .claude/settings.json) | partial | **PI-IDFILE-001** with `weight_override: 1.00` | — |
| Unpinned deps in `requirements.txt`, `package.json`, `pyproject.toml` | yes | — | — |
| **PEP-723 inline-deps without `==` pin** | no (Cisco doesn't surface as discrete) | **PI-PEP723-001** | — |
| Typosquatting on package names | yes | — | — |
| Dependency confusion | yes | — | — |
| `curl … \| bash`, `wget … \| sh`, `iwr … \| iex` | yes | — | — |
| Compiled bytecode (`.pyc`) shipped in scripts/ | yes (bytecode analyzer) | — | — |
| Bash taint flow (source → transform → sink) | yes | — | — |
| Office macros, polyglot files in assets/ | yes (YARA + macro pass) | — | — |
| Network egress to webhooks / pastebins / discord | yes | — | — |
| Frontmatter spec conformance (agentskills.io) | no (out of Cisco's scope) | **FC001** name kebab-case + publisher-token forbid | — |
| Frontmatter spec conformance — description length | no | **FC002** 1–1024 chars | — |
| Frontmatter spec conformance — top-level field whitelist | no | **FC003** custom fields under `metadata:` | — |
| Coroboros house rule — `metadata.version` forbidden | no | **FC004** | — |
| Frontmatter spec conformance — `license` SPDX validity | no | **FC005** with built-in ~30 OSS-SPDX list | proprietary-license strings outside the list (see `docs/fp-audit.md` tracking note 2) |
| Secrets — API keys, SSH keys, tokens | wrapped via `gitleaks` | — | — |
| Workflow safety — `.github/workflows/` of audited repo | wrapped via `actionlint` | — | — |
| Repo-posture signals (LICENSE, CODEOWNERS, branch protection, SBOM, signed commits) | wrapped via OpenSSF Scorecard | — | — |
| **Trust artefact — signed report bundle** | no (Cisco emits SARIF only) | **`actions/attest-build-provenance` + `actions/attest-sbom`** under public-good Sigstore + GitHub OIDC | — |
| **Pruner Verified badge** | no | yes (Coroboros design tokens, no gradient/shadow/rounded) | — |
| Behavioral red flags — delayed activation, weekday-keyed triggers | partial (Cisco behavioral pass) | — | full semantic latent-activation detection (out of static scope) |
| Memory poisoning via instructions writing to MEMORY.md, SOUL.md | yes | **PI-IDFILE-001** as discrete | — |
| Transitive trust (`install all recommended_skills`) | partial | — | full transitive-trust verification (deferred to post-1.0) |
| Eval poisoning in self-shipped test cases | yes | — | — |
| Prompt-defense posture — defensive language presence on generalist agents | no (Cisco doesn't reverse-detect) | **PD001–PD012** (opt-in) | — |
| MCP server CVE references (CVE-2025-53107 etc.) | partial — Snyk has the strongest coverage here | flag-only | full MCP-runtime probe (out of v0.1 scope) |
| Agent-side red teaming (garak / promptfoo / PyRIT) | n/a | n/a | full live-LLM probing (deferred to post-1.0 — needs a harness) |
| LLM-call-from-the-scanner | Cisco `--use-llm` opt-in upstream | Pruner stays deterministic at 0.1.0 | — |
| EU AI Act regulatory signal | n/a | descriptive mapping to OWASP AST/LLM | prescriptive certification (we attest, we do not certify) |

## Footnotes

- **"yes"** in the Cisco column means Cisco's published 13-pass analyzer covers the class; Pruner adds nothing on top.
- **"partial"** means coverage exists but is incomplete or not surfaced as a discrete signal — Pruner's pack adds the discrete layer.
- **"no"** means Cisco does not address it; the Coroboros pack is the only line of defense within Pruner.
- **"Nothing covers"** is the honest negative space at v0.1.0. Each gap is either a deferred-by-decision item (post-1.0 scope) or fundamentally beyond static analysis (semantic latent activation).
