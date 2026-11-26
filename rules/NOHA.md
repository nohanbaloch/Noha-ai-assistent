# Noha AI Assistant Agent Rules & Guidelines

When the `noha-ai-assistent` plugin is enabled, follow these guidelines:

## 1. Interactive UI Panel Trigger
Whenever the user asks to see the Noha model switcher, opens `/noha`, `/assistant`, or asks to "show model list", "switch models", or "open Noha AI panel":
- Copy or write `widget.html` from `plugins/noha-ai-assistent/assets/widget.html` into `<appDataDir>/brain/<conversation-id>/noha_widget.html` with `ArtifactMetadata: {UserFacing: true, RequestFeedback: false}`.
- Embed it inline in the chat using:
  ```html
  <agent-embed src="file:///<appDataDir>/brain/<conversation-id>/noha_widget.html"></agent-embed>
  ```
- Present a concise 1-sentence status of the currently active model and provider.

## 2. Provider Routing Heuristics
- **⚡ Groq LPU**:
  - Use when the user requests "fast", "instant", "Groq", "Llama 3.3 on Groq", or needs rapid generation (~800 tokens/sec).
  - Use `groq_chat` with `llama-3.3-70b-versatile` (flagship) or `deepseek-r1-distill-llama-70b` (reasoning) or `llama-3.1-8b-instant` (triage).
- **🌐 OpenRouter**:
  - Use when the user explicitly mentions Claude (`anthropic/claude-sonnet-5.5`, `anthropic/claude-3.7-sonnet`), DeepSeek R1 (`deepseek/deepseek-r1`), OpenAI (`openai/o3-mini`, `openai/gpt-4o`), or asks to search the 470+ models catalog.
  - Use `openrouter_chat` or `openrouter_compare_models`.
- **🎯 AgentRouter**:
  - Use when the user asks to delegate tasks to autonomous domain specialists (`coding`, `reasoning`, `fast`, `review`).
  - Use `agentrouter_route_task`.
- **⚖️ Cross-Provider Comparison**:
  - When the user asks to compare models across providers (e.g. Groq vs Claude vs DeepSeek), call `noha_compare_providers`.

## 3. Transparency & Attribution
- Always cite the active provider and model in the response header (e.g., "⚡ *According to Groq Llama 3.3 70B (350 t/s)...*" or "🌐 *According to Claude Sonnet 5.5 via OpenRouter...*").
- If `GROQ_API_KEY` or `OPENROUTER_API_KEY` is missing when requested, politely inform the user and provide the link to obtain the key.

## 4. API Key Management from Panel & Chat
- When the user supplies or asks to configure an API key for Groq, OpenRouter, or AgentRouter (e.g. from the panel's "Apply to .env" button or typing "Save groq API key: ..."):
  - Invoke the `noha_save_api_key` tool with the corresponding `provider` and `api_key`.
  - Confirm the key is safely stored in `.env` and immediately active.
