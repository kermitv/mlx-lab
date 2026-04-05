# Project State & Roadmap: Transition to Ollama/Gemma 4

## Current Status: **Active Migration**
The project is currently in a state of transition. We are moving away from an MLX-centric inference architecture toward a more robust, interoperable, and stable ecosystem centered around **Ollama**, **gemma4:26b**, and **OpenCode.ai**.

The "MLX Lab" (as documented in the root README) is being re-contextualized into the "Ollama/OpenCode Lab."

## The Pivot: Why We Are Moving
While the MLX-based (Qwen) architecture provided excellent raw performance, testing revealed:
- **Integration Friction:** Difficulty maintaining stable, seamless interactions between MLX-LM and complex agentic tools (e.g., OpenCode.ai).
- **Complexity Overload:** Managing multiple Python environments and manual server configurations for MLX was becoming a bottleneck for rapid experimentation.
- **The Gemma 4 Advantage:** Initial validation with **gemma4:26b** via Ollama has shown superior reasoning capabilities and a much more "plug-and-play" operational profile for local coding tasks.

## Active Workstreams

### 1. Infrastructure Stabilization
*   **Goal:** Establish the Ollama runtime as the canonical service on `oc-mac-m5`.
*   **Key Task:** Standardize the `run_config.json` patterns for Ollama model pulls and serving.

### 2. Benchmarking (The "Run 5" Initiative)
*   **Goal:** Produce a scientific, "apples-to-apples" comparison between the MLX/Qwen baseline and the Ollama/Gemma 4 stack.
*   **Key Task:** Implement the new benchmark harness logic to ingest Ollama API outputs.

### 3. OpenCode.ai Integration
*   **Goal:** Use OpenCode.ai as the primary orchestration layer for codebase management and agentic execution.
*   **Key Task:** Validate tool-calling stability using the new gemma4-based endpoint.

## Roadmap

| Milestone | Description | Priority |
| :--- | :--- | :--- |
| **Phase 1: Documentation** | Finalize the Transition Plan and update all legacy README references. | **High** |
| **Phase 2: Infrastructure** | Provision and validate Ollama/Gemma 4 stability on the host. | **High** |
| **Phase 3: Run 5 Execution**| Run the comparative benchmark and generate new performance charts. | **Medium** |
| **Phase 4: Integration** | Fully integrate OpenCode.ai into the automated testing pipeline. | **Medium** |

## Resource Links
- [Detailed Transition Plan](./transition-plan-ollama.md)
- [Historical MLX Benchmarks](./benchmarks/run4/)
- [Current Model Inventory](./docs/notes/model-inventory-audit-2026-04-02.md)

---
*Last Updated: 2026-04-03*
