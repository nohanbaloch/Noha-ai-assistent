# 🚀 Noha AI Assistant for Antigravity IDE (VS Code)

<div align="center">

[![Antigravity Plugin](https://img.shields.io/badge/Antigravity-Plugin-blue?style=for-the-badge&logo=google)](https://github.com)
[![Groq LPU](https://img.shields.io/badge/Groq-LPU%20Ultra--Fast%20(~800%20tps)-orange?style=for-the-badge&logo=fastapi)](https://groq.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-470%2B%20Frontier%20Models-purple?style=for-the-badge&logo=openai)](https://openrouter.ai)
[![AgentRouter](https://img.shields.io/badge/AgentRouter-Specialist%20Agents-emerald?style=for-the-badge)](https://agentrouter.to)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

**The ultimate AI Assistant and Model Selector for Antigravity IDE (VS Code). Seamlessly switch between Groq LPU (ultra-fast sub-second responses), OpenRouter (470+ frontier LLMs), and AgentRouter (autonomous specialists) with an Antigravity-native model list drawer.**

[Interactive Model Drawer](#-antigravity-native-model-drawer) • [Key Features](#-key-features) • [Quick Start](#-quick-start) • [Supported Models](#-supported-models--providers) • [MCP Tools](#️-provided-mcp-tools) • [Setup](#-setup--configuration)

</div>

---

## 📸 Antigravity-Native Model Drawer

Type `/noha` or `/assistant` anywhere in Antigravity chat to toggle the visual model selector:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🚀 NOHA AI ASSISTANT                    ACTIVE: ⚡ Groq / llama-3.3-70b     │
├─────────────────────────────────────────────────────────────────────────────┤
│ [⚡ Groq LPU (Ultra-Fast)]  [🌐 OpenRouter (470+)]  [🎯 AgentRouter Roles]   │
│ 🔍 [Search models, tags, or capabilities...                               ] │
├─────────────────────────────────────────────────────────────────────────────┤
│  ⚡ Llama 3.3 70B Versatile  [★ Flagship]    ⚡ DeepSeek R1 Distill [🧠 Logic]│
│  Meta • ~350 t/s • 128k ctx                 DeepSeek 70B • ~320 t/s • 128k  │
│                                                                             │
│  🚀 Llama 3.1 8B Instant   [850 t/s]        🌐 Claude Sonnet 5.5   [★ Code] │
│  Meta • Ultra-Fast Triage • 128k ctx        Anthropic • 200k ctx • $3/1M    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Custom ID: [ e.g. llama-3.3-70b-specdec                      ] [Apply ID]   │
│ Target: groq:llama-3.3-70b-versatile    [⚖️ Compare] [📋 Copy] [🎯 Use Active] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Features

- ⚡ **Groq LPU Hardware Acceleration**: Run queries on Groq's Language Processing Units (LPUs) at blistering speeds of **350–850 tokens/second**, with full support for reasoning traces (`<think>` tags).
- 🌐 **OpenRouter 470+ Frontier Catalog**: Switch on demand to Claude 3.7 Sonnet, DeepSeek R1, GPT-4o, OpenAI o3-mini, and open-weights models.
- 🎯 **AgentRouter Autonomous Specialists**: Intelligently dispatch complex tasks to domain-tuned agent personas (`coding`, `reasoning`, `fast triage`, `security auditor`).
- 🎛️ **Antigravity-Styled Interactive Model Drawer (`/noha`)**: A sleek in-chat control center styled to match Antigravity IDE and VS Code with live search, model tags, context metrics, and one-click switching.
- 💾 **Persistent Active Selection**: Switch models once in the UI or chat, and Noha remembers your preferred model across all sessions via `active_selection.json`.
- ⚖️ **Cross-Provider Benchmarking**: Send the same prompt simultaneously to Groq, OpenRouter, and AgentRouter to evaluate speed vs. reasoning depth.
- 🤖 **Dedicated `@noha-assistant` Subagent**: Spawn an autonomous subagent for background multi-model reviews and deep code generation.

---

## ⚡ Quick Start

### 1. Open the Model Drawer
Type the slash command in chat:
```text
/noha
```
*(or `/assistant`)*. Select your desired provider and model, then click **"Use Active Model"** or **"Compare Providers"**.

### 2. Natural Language Queries
Noha AI Assistant automatically routes your requests based on provider and intent:
- **Groq Ultra-Fast Query:**
  > *"Ask Groq Llama 3.3 to write a high-performance LRU cache in TypeScript."*
- **Reasoning with DeepSeek on Groq:**
  > *"Ask Groq DeepSeek R1 distill to solve this combinatorial optimization problem step-by-step."*
- **Frontier Architecture with Claude:**
  > *"Ask Claude Sonnet 5.5 on OpenRouter to review our event-driven microservices architecture."*
- **Benchmark Across Providers:**
  > *"Compare how Groq Llama 3.3, Claude Sonnet 5.5, and DeepSeek R1 implement a concurrent worker pool."*

### 3. Delegate to the `@noha-assistant` Subagent
```text
@noha-assistant Benchmark our database schema against OpenRouter Claude and Groq DeepSeek R1, highlighting potential index bottlenecks.
```

---

## 🤖 Supported Models & Providers

| Provider | Model Preset | Speed / Latency | Context | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **⚡ Groq LPU** | `llama-3.3-70b-versatile` | ~350 tokens/s | 128k | Flagship code, architecture, system design |
| **⚡ Groq LPU** | `deepseek-r1-distill-llama-70b` | ~320 tokens/s | 128k | Deep reasoning, mathematical logic, proofs |
| **⚡ Groq LPU** | `llama-3.1-8b-instant` | **~850 tokens/s** | 128k | Instant triage, regex, fast summarization |
| **⚡ Groq LPU** | `mixtral-8x7b-32768` | ~500 tokens/s | 32k | Mixture of Experts architecture |
| **⚡ Groq LPU** | `whisper-large-v3` | Real-time | Audio | Speech-to-text audio transcription |
| **🌐 OpenRouter** | `anthropic/claude-sonnet-5.5` | ~50 tokens/s | 200k | Top-tier full-stack coding & refactoring |
| **🌐 OpenRouter** | `deepseek/deepseek-r1` | ~30 tokens/s | 128k | Leading open-weight reasoning model |
| **🌐 OpenRouter** | `openai/o3-mini` | ~80 tokens/s | 128k | OpenAI STEM & multi-step logic |
| **🌐 OpenRouter** | `particle-ai/particle-1:free` | ~40 tokens/s | 32k | **100% Free** agentic code generation |
| **🎯 AgentRouter** | `coding` / `reasoning` / `fast` | Autonomous | Dynamic | Domain-specialized autonomous routing |

---

## 🛠️ Provided MCP Tools

| MCP Tool | Primary Arguments | Description |
| :--- | :--- | :--- |
| **`noha_status`** | *(none)* | Checks connectivity, active model selection, and API keys for Groq, OpenRouter, and AgentRouter. |
| **`noha_save_api_key`** | `provider`, `api_key` | Save or update API key for Groq, OpenRouter, or AgentRouter; updates `.env` instantly. |
| **`noha_switch_model`** | `provider`, `model`, `role` | Switch active provider and model; persists state in `active_selection.json`. |
| **`noha_chat`** | `prompt`, `provider`, `model`, `max_tokens` | Prompt execution on the currently active model (Groq, OpenRouter, or AgentRouter). |
| **`groq_chat`** | `prompt`, `model`, `temperature`, `max_tokens` | Ultra-fast Groq LPU completion with latency & tokens/sec metrics. |
| **`groq_list_models`** | *(none)* | Live query of available models on Groq Cloud LPU. |
| **`openrouter_chat`** | `model`, `prompt`, `temperature`, `max_tokens` | Direct completion via OpenRouter's 470+ frontier model catalog. |
| **`openrouter_list_models`** | `query`, `limit` | Live search across OpenRouter models with real-time pricing and context limits. |
| **`openrouter_compare_models`**| `models` (array), `prompt` | Parallel multi-model evaluation across OpenRouter models. |
| **`agentrouter_route_task`** | `task`, `category`, `preferred_provider` | Autonomous task routing to domain specialists (`coding`, `reasoning`, `fast`, `review`). |
| **`noha_compare_providers`** | `prompt` | Simultaneous multi-provider benchmark across Groq LPU, DeepSeek R1, and OpenRouter Claude. |

---

## 🔑 Setup & Configuration

Add your API keys to `.env` in the plugin root:

```env
# Groq Cloud API Key (https://console.groq.com/keys)
GROQ_API_KEY=gsk_...

# OpenRouter API Key (https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-...

# AgentRouter API Key (https://agentrouter.to) - Optional
AGENTROUTER_API_KEY=sk-...

# Default Active Model
NOHA_ACTIVE_PROVIDER=groq
NOHA_ACTIVE_MODEL=llama-3.3-70b-versatile
```

---

## 📄 License

MIT License — Built for the Antigravity Community.
