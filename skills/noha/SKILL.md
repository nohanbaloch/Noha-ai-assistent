---
name: noha
description: Noha AI Assistant & Model Switcher. Switch seamlessly between Groq LPU, OpenRouter, and AgentRouter with an Antigravity-styled model list and control center.
---

# Noha AI Assistant Interactive Control Center

Use this skill whenever the user invokes `/noha`, `/assistant`, asks to "open Noha AI", or wants to view and switch models between Groq, OpenRouter, and AgentRouter.

## Mandatory Execution Step: Render the Interactive Model Drawer

Whenever this skill is triggered, you **MUST ALWAYS** render the visual model selection drawer:

1. Write or copy the widget file to the current conversation's artifact directory:
   `<appDataDir>/brain/<conversation-id>/noha_widget.html`
   (Content is sourced from the plugin's `assets/widget.html`).
   Always provide `ArtifactMetadata` with `UserFacing: true` and `RequestFeedback: false`.

2. Immediately embed the widget inline in your chat reply using:
   ```html
   <agent-embed src="file:///<appDataDir>/brain/<conversation-id>/noha_widget.html"></agent-embed>
   ```

3. Call `noha_status` to report active provider, model, and connectivity status.
