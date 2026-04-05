# Transition Plan: MLX to Ollama/OpenCode Ecosystem

## Overview
This document outlines the strategic pivot from the MLX-based inference infrastructure to a more stable and interoperable ecosystem centered around **Ollama**, **gemma4:26b**, and **OpenCode.ai** for codebase management.

## Rationale for Transition
After extensive benchmarking and integration testing (notably in Runs 1-4), several critical limitations were identified in the MLX implementation:
- **Tool Interoperability:** Difficulty in maintaining seamless integration between MLX-LM servers and external development agents/tools.
- **Runtime Stability:** Challenges in maintaining a consistent, reproducible environment for complex, multi-file repair tasks.
- **Ecosystem Maturity:** The Ollama runtime provides a more robust, OpenAI-compatible standard that integrates more natively with the current toolset.

## Objectives
1. **Stabilize Ollama Infrastructure:** Establish a canonical, reproducible local inference service.
2. **Standardize Model Deployment:** Use `gemma4:2/gemma4:26b` as the primary reasoning and coding model.
3. **Implement OpenCode.ai:** Integrate OpenCode.ai as the primary orchestration and codebase management layer.
4. **Knowledge Preservation:** Document all "fact-finding" and "runbook" data gathered during the MLX era to prevent loss of operational intelligence.

## Phases of Migration

### Phase 1: Documentation & Planning (In Progress)
- [ ] Formalize the Transition Plan (this document).
- [ ] Audit existing MLX runbook data and move insights to the new ecosystem docs.
- [ ] Define the new "Canonical Environment" parameters for Ollama.

### Phase 2: Infrastructure Setup
- [ ] Configure the Ollama service on `oc-mac-m5`.
- [ ] Validate `gemma4:26b` serving capabilities.
- [ ] Setup OpenCode.ai integration for local repository management.

### Phase 3: Validation & Benchmarking
- [ ] Execute "Run 5" (the Transition Benchmark) comparing MLX vs. Ollama.
- [ ] Verify tool-calling/agentic workflows (e.g., Aider, OpenCode) against the new stack.

## Artifacts & Reference Data
*Note: All historical data from the MLX era will be preserved in the `docs/migration/historical/` directory for audit purposes.*

- **Historical Runbooks:** `docs/migration/historical/mlx-runbook-v1.md` (to be moved)
- **Benchmark Evidence:** `benchmarks/run4/` (maintained for comparative analysis)
- **Fact-Finding Logs:** (To be consolidated here)

---
*Last Updated: 2026-04-03*
