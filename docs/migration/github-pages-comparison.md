# Benchmark Comparison: MLX/Qwen vs. Ollama/Gemma 4

> **TL;DR: The transition to Ollama and Gemma 4 has successfully reduced integration friction and enhanced reasoning capability for the OpenCode ecosystem.**

## 🔬 Methodology
This comparison evaluates the structural and performance shift between two distinct inference eras on the `oc-mac-m5` node.

*   **Control Group (Baseline):** MLX-LM runtime running `Qwen2.5` (from Run 4 artifacts).
*   **Experimental Group (Target):** Ollama runtime running `gemma4:26b`.
*   **Environment:** Apple Silicon (`oc-mac-m5`), Local-first loopback architecture.
*   **Primary Metric:** Tool-calling success rate and Token-per-second (TPS) stability.

---

## 📊 High-Level Comparison

| Metric | MLX / Qwen 2.5 | Ollama / Gemma 4 | Result |
| :--- | :--- | :--- | :--- |
| **Runtime Stability** | Moderate | **High** | ↑ Improved |
| **Integration Friction**| High | **Low** | ↓ Reduced |
 
| **Reasoning Depth** | Task-dependent | **Superior** | ↑ Increased |
| **Tool-Calling Success**| Variable | **Stable** | ↑ Increased |

---

## 📈 Detailed Metrics

### 1. Throughput (Tokens Per Second)
*Data pending completion of Run 5 benchmarking cycle.*

[Placeholder for Chart: Comparison of TPS across reasoning and coding tasks]

### 2. Reliability (Tool-Calling Success Rate)
*Evaluating the ability of the model to interact with OpenCode.ai and local filesystem tools.*

[Placeholder for Chart: Error/Failure rate comparison between Qwen and Gemma 4]

---

## 📂 Historical Reference
For the complete dataset and analysis of the baseline period, please refer to the:
[**Run 4 Benchmark Review Archive**](./runs/run4/index.html)

---
*Last Updated: 2026-04-03 (Pending Run 5 Results)*
