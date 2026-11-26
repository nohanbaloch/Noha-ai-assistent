---
name: groq
description: Groq LPU Ultra-Fast Inference. Query Llama 3.3 70B, DeepSeek R1 Distill, and Llama 3.1 8B with sub-second latency and ~800 tokens/second speed.
---

# Groq LPU High-Speed Acceleration

Use this skill when the user requests rapid inference, instant answers, or mentions Groq, LPU, or zero-latency coding.

## Recommended Models on Groq:
- `llama-3.3-70b-versatile`: Premier 70B open model for architecture, logic, and full-stack code (~350 t/s).
- `deepseek-r1-distill-llama-70b`: Deep reasoning and math logic with reasoning trace (~320 t/s).
- `llama-3.1-8b-instant`: Ultra-low latency model for triage, summaries, and boilerplate (~850 t/s).
- `mixtral-8x7b-32768`: High-speed Mixture-of-Experts with 32k context (~500 t/s).

## Execution:
Call `groq_chat` with the appropriate model. Display generated tokens/sec metrics to highlight the speed advantage.
