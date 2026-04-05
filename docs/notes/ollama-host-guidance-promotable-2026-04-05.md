# Ollama Host Guidance Promotable Extract (2026-04-05)

Status: extraction candidate, not yet adopted
Date: 2026-04-05
Derived from: [ollama-host-guidance-review-2026-04-05.md](/Users/kermitv/dev/mlx-lab/docs/notes/ollama-host-guidance-review-2026-04-05.md)
Intent: isolate the parts of the reviewed Ollama guidance that could later be promoted into migration or operator docs

## Purpose

This note extracts the parts of the reviewed Ollama guidance that appear durable enough to reuse later. It is intentionally narrower than the source review note and excludes the more promotional, comparative, or time-sensitive claims.

## Candidate Guidance

### Local Host Posture

This machine can be treated as a capable local inference host rather than only a single-user client. That framing is useful because it clarifies that local LLM infrastructure here may serve multiple downstream consumers, including scripts, local tools, and browser-based interfaces.

### Serving Surfaces

The Ollama runtime can be understood through three distinct serving surfaces:

1. API serving
2. web UI serving
3. editor or developer-tool integration

This separation is useful because it keeps the runtime itself distinct from the downstream interfaces that consume it.

### API Surface

The local Ollama API is the most direct and automatable serving surface. It is the right place to document:

- loopback-first usage
- simple local automation examples
- downstream client reuse
- the distinction between the runtime and the tools that call it

### Web UI As Optional Consumer

A chat-style web UI such as Open WebUI is best treated as an optional downstream consumer of the local runtime rather than part of the runtime definition itself.

That framing keeps:

- the Ollama daemon as the core local service
- the web interface as one possible operator-facing consumer

### Editor Integration As Optional Consumer

Editor integrations should also be documented as optional downstream consumers. Their relevance is operational convenience, not architecture ownership.

This distinction matters because it prevents any one editor or plugin from becoming the implied canonical control plane.

### Evaluation Pack Concept

The most reusable idea in the model curriculum is not the exact pack, but the evaluation pattern:

- include a reasoning-oriented model
- include a coding-oriented model
- include a multimodal model if relevant
- include a smaller fast-response model
- compare models by role rather than assuming one universal default

This idea is likely promotable if rewritten with locally validated examples.

## What Was Intentionally Excluded

The following were intentionally not extracted for promotion:

- exact model recommendations as stable repo policy
- comparative quality claims about specific architectures
- language implying that Open WebUI or Continue.dev are required
- wording that assumes local network exposure should be the default

## Best Future Landing Zones

If promoted later, the likely destinations are:

- [current-state-and-roadmap.md](/Users/kermitv/dev/mlx-lab/docs/migration/current-state-and-roadmap.md) for the high-level runtime direction
- [ollama-system-daemon-setup.md](/Users/kermitv/dev/mlx-lab/docs/migration/ollama-system-daemon-setup.md) for serving-surface guidance

## Promotion Constraints

Before promotion, the extracted guidance should be rewritten so that it is:

- repo-specific
- local-first and security-aware
- free of time-sensitive hype language
- explicit about what is optional versus canonical
