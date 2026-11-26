#!/usr/bin/env python3
"""
Noha AI Assistant MCP Server for Antigravity IDE (VS Code).
Provides unified access to Groq LPU, OpenRouter, and AgentRouter with:
- Antigravity-styled model management
- Ultra-low latency LPU execution via Groq
- Frontier reasoning via OpenRouter (Claude 3.7 / DeepSeek R1 / GPT-4o)
- Autonomous specialist agent dispatch via AgentRouter
- Parallel multi-model & multi-provider evaluation
"""

import sys
import os
import json
import re
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def get_base_dirs():
    return [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.getcwd(),
        os.path.expanduser("~")
    ]

def load_dotenv():
    """Load environment variables from .env files in search paths."""
    for d in get_base_dirs():
        env_file = os.path.join(d, ".env")
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip("'\"")
                            if key and val and not val.startswith("your_"):
                                os.environ[key] = val
            except Exception as e:
                sys.stderr.write(f"Error reading {env_file}: {e}\n")

load_dotenv()

# State persistence for active provider and model
def get_state_file_path():
    plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(plugin_dir, "active_selection.json")

def update_env_file(key_name, key_value):
    """Update or insert key_name in .env files across search dirs."""
    updated_files = []
    for d in get_base_dirs():
        env_file = os.path.join(d, ".env")
        if os.path.exists(env_file):
            lines = []
            found = False
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith(f"{key_name}=") or stripped.startswith(f"#{key_name}="):
                            lines.append(f"{key_name}={key_value}\n")
                            found = True
                        else:
                            lines.append(line)
                if not found:
                    lines.append(f"{key_name}={key_value}\n")
                with open(env_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                updated_files.append(env_file)
            except Exception as e:
                sys.stderr.write(f"Error updating {env_file}: {e}\n")
    os.environ[key_name] = key_value
    return updated_files

def load_active_state():
    state_file = get_state_file_path()
    default_state = {
        "provider": os.environ.get("NOHA_ACTIVE_PROVIDER", "groq"),
        "model": os.environ.get("NOHA_ACTIVE_MODEL", "llama-3.3-70b-versatile"),
        "role": "coding"
    }
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_state.update(saved)
        except Exception:
            pass
    return default_state

def save_active_state(provider, model, role="coding"):
    state = {
        "provider": provider,
        "model": model,
        "role": role,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    state_file = get_state_file_path()
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"Error saving state to {state_file}: {e}\n")
    return state

# API Key Getters
def get_groq_key(explicit=None):
    load_dotenv()
    return explicit or os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_KEY")

def get_openrouter_key(explicit=None):
    load_dotenv()
    return explicit or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPEN_ROUTER_API_KEY")

def get_agentrouter_key(explicit=None):
    load_dotenv()
    return explicit or os.environ.get("AGENTROUTER_API_KEY") or os.environ.get("AGENT_ROUTER_API_KEY")

def make_request(url, headers, data=None, method="GET", timeout=60):
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_msg)
            return {"error": err_json.get("error", err_json), "status_code": e.code}
        except Exception:
            return {"error": err_msg or str(e), "status_code": e.code}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------------------------------------
# Tool 1: noha_status
# -------------------------------------------------------------
def tool_noha_status(args):
    groq_k = get_groq_key()
    or_k = get_openrouter_key()
    ar_k = get_agentrouter_key()
    state = load_active_state()

    lines = [
        "# ⚡ Noha AI Assistant — Status & Configuration",
        "",
        "### 🎯 Active Selection",
        f"- **Current Provider**: `{state.get('provider')}`",
        f"- **Active Model / Role**: `{state.get('model')}`",
        "",
        "### 🔌 Provider Connectivity",
        f"- **⚡ Groq Cloud LPU**: {'✅ Configured' if groq_k else '⚠️ Key missing (set GROQ_API_KEY in .env)'}",
        f"- **🌐 OpenRouter (470+ models)**: {'✅ Configured' if or_k else '❌ Key missing (set OPENROUTER_API_KEY in .env)'}",
        f"- **🎯 AgentRouter Specialists**: {'✅ Configured' if ar_k else '⚠️ Optional (falls back to OpenRouter heuristics)'}",
        "",
        "### 🚀 Model Highlights",
        "- **Groq LPU (Ultra-Fast ~800 tps)**:",
        "  - `llama-3.3-70b-versatile`: Flagship general intelligence & coding",
        "  - `deepseek-r1-distill-llama-70b`: Ultra-fast reasoning & math with `<think>` traces",
        "  - `llama-3.1-8b-instant`: Instant low-latency triage & scripts",
        "- **OpenRouter (Frontier Depth)**:",
        "  - `anthropic/claude-sonnet-5.5`: System architecture & advanced refactoring",
        "  - `deepseek/deepseek-r1`: Full open-weight reasoning model",
        "  - `openai/o3-mini`: Speed reasoning for logic & math",
        "- **AgentRouter (Specialists)**: `coding`, `reasoning`, `fast`, `review`, `creative`",
        "",
        "> [!TIP]",
        "> Run `/noha` in Antigravity chat to toggle the visual model selector drawer."
    ]

    return "\n".join(lines)

# -------------------------------------------------------------
# Tool 2: noha_switch_model
# -------------------------------------------------------------
def tool_noha_switch_model(args):
    provider = (args.get("provider") or "").lower().strip()
    model = (args.get("model") or "").strip()
    role = args.get("role", "coding")

    if not provider or provider not in ["groq", "openrouter", "agentrouter"]:
        return "⚠️ Error: 'provider' must be one of: 'groq', 'openrouter', 'agentrouter'."

    if not model:
        if provider == "groq":
            model = "llama-3.3-70b-versatile"
        elif provider == "openrouter":
            model = "anthropic/claude-sonnet-5.5"
        elif provider == "agentrouter":
            model = role

    saved = save_active_state(provider, model, role)
    return (
        f"✅ **Noha AI Assistant active model updated!**\n\n"
        f"- **Provider**: `{saved['provider']}`\n"
        f"- **Model**: `{saved['model']}`\n"
        f"- **Role**: `{saved['role']}`\n\n"
        f"Subsequent prompts sent via `noha_chat` will use this model."
    )

# -------------------------------------------------------------
# Tool 3: noha_save_api_key
# -------------------------------------------------------------
def tool_noha_save_api_key(args):
    provider = (args.get("provider") or "").lower().strip()
    key = (args.get("api_key") or "").strip()

    if not provider or not key:
        return "⚠️ Error: Both 'provider' ('groq', 'openrouter', or 'agentrouter') and 'api_key' are required."

    mapping = {
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "agentrouter": "AGENTROUTER_API_KEY"
    }
    env_var = mapping.get(provider)
    if not env_var:
        return f"⚠️ Error: Unknown provider '{provider}'. Must be 'groq', 'openrouter', or 'agentrouter'."

    updated = update_env_file(env_var, key)
    masked = key[:6] + "..." + key[-4:] if len(key) > 12 else "***"
    return (
        f"✅ **{provider.upper()} API Key saved successfully!**\n\n"
        f"- **Variable**: `{env_var}`\n"
        f"- **Key Value**: `{masked}`\n"
        f"- **Updated Environment/Files**: {', '.join([os.path.basename(f) for f in updated]) if updated else '.env runtime'}\n\n"
        f"You can now immediately execute queries with `{provider}`."
    )

# -------------------------------------------------------------
# Tool 3: groq_chat
# -------------------------------------------------------------
def tool_groq_chat(args):
    model = args.get("model") or "llama-3.3-70b-versatile"
    prompt = args.get("prompt")
    system_prompt = args.get("system_prompt")
    temperature = args.get("temperature", 0.7)
    max_tokens = args.get("max_tokens", 4096)
    api_key = get_groq_key(args.get("api_key"))

    if not api_key:
        return (
            "⚠️ Error: GROQ_API_KEY is not configured.\n\n"
            "Please configure your Groq key:\n"
            "1. Add `GROQ_API_KEY=gsk_...` to `.env` in the plugin or workspace folder.\n"
            "2. Or pass `api_key` directly in the tool arguments.\n"
            "Get a free instant API key at: https://console.groq.com/keys"
        )

    if not prompt:
        return "⚠️ Error: 'prompt' is required."

    url = "https://api.groq.com/openai/v1/chat/completions"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Noha-AI-Assistant/1.0"
    }

    t0 = time.time()
    res = make_request(url, headers, data=payload, method="POST", timeout=60)
    latency = time.time() - t0

    if "error" in res:
        return f"⚠️ Groq LPU Error ({res.get('status_code', 'unknown')}): {json.dumps(res['error'], indent=2)}"

    try:
        choice = res["choices"][0]
        msg = choice.get("message", {})
        content = msg.get("content") or ""
        
        usage = res.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        tps = (completion_tokens / latency) if latency > 0 else 0

        # Handle DeepSeek R1 reasoning tags <think> ... </think>
        reasoning = ""
        think_match = re.search(r"<think>(.*?)</think>", content, flags=re.DOTALL)
        if think_match:
            reasoning = think_match.group(1).strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        header = (
            f"### ⚡ Groq LPU: `{model}`\n"
            f"*(Generated in {latency:.2f}s • ~{tps:.0f} tokens/s • {prompt_tokens} prompt / {completion_tokens} completion tokens)*\n\n"
        )

        body = ""
        if reasoning:
            body = f"<details><summary>🧠 Thought Process (DeepSeek Reasoning)</summary>\n\n{reasoning}\n\n</details>\n\n{content}"
        else:
            body = content

        return header + body
    except Exception as e:
        return f"⚠️ Error parsing Groq response: {e}\nRaw payload:\n{json.dumps(res, indent=2)}"

# -------------------------------------------------------------
# Tool 4: groq_list_models
# -------------------------------------------------------------
def tool_groq_list_models(args):
    api_key = get_groq_key(args.get("api_key"))
    if not api_key:
        # Return standard curated list if key not yet added
        return (
            "### ⚡ Groq LPU Recommended Models (Key not yet set):\n\n"
            "- **`llama-3.3-70b-versatile`**: Flagship 70B model with 128k context (~350 t/s)\n"
            "- **`deepseek-r1-distill-llama-70b`**: DeepSeek R1 reasoning model on 70B Llama (~320 t/s)\n"
            "- **`llama-3.1-8b-instant`**: Ultra-fast 8B model with 128k context (~850 t/s)\n"
            "- **`mixtral-8x7b-32768`**: Mixture of experts with 32k context (~500 t/s)\n"
            "- **`gemma2-9b-it`**: Google Gemma 2 9B instruction tuned (~420 t/s)\n"
            "- **`whisper-large-v3`**: OpenAI Whisper speech-to-text transcription\n\n"
            "*Add `GROQ_API_KEY` to query live models dynamically from `https://api.groq.com/openai/v1/models`.*"
        )

    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Noha-AI-Assistant/1.0"
    }

    res = make_request(url, headers, method="GET", timeout=20)
    if "error" in res:
        return f"⚠️ Error fetching Groq models: {res['error']}"

    models = res.get("data", [])
    output = [f"### ⚡ Available Groq Models ({len(models)} models available):\n"]
    for m in models:
        mid = m.get("id")
        owner = m.get("owned_by", "groq")
        ctx = m.get("context_window", "N/A")
        output.append(f"- **`{mid}`** (Context: {ctx} | Owner: `{owner}`)")

    return "\n".join(output)

# -------------------------------------------------------------
# Tool 5: openrouter_chat
# -------------------------------------------------------------
def tool_openrouter_chat(args):
    model = args.get("model") or "anthropic/claude-sonnet-5.5"
    prompt = args.get("prompt")
    system_prompt = args.get("system_prompt")
    temperature = args.get("temperature", 0.7)
    max_tokens = args.get("max_tokens", 4096)
    api_key = get_openrouter_key(args.get("api_key"))

    if not api_key:
        return (
            "⚠️ Error: OPENROUTER_API_KEY is not configured.\n\n"
            "Set `OPENROUTER_API_KEY` in `.env` or pass `api_key` in arguments.\n"
            "Get an API key at https://openrouter.ai/keys"
        )

    if not prompt:
        return "⚠️ Error: 'prompt' is required."

    url = "https://openrouter.ai/api/v1/chat/completions"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://antigravity.google",
        "X-Title": "Noha AI Assistant",
        "Content-Type": "application/json",
        "User-Agent": "Noha-AI-Assistant/1.0"
    }

    t0 = time.time()
    res = make_request(url, headers, data=payload, method="POST", timeout=120)
    latency = time.time() - t0

    if "error" in res:
        return f"⚠️ OpenRouter Error ({res.get('status_code', 'unknown')}): {json.dumps(res['error'], indent=2)}"

    try:
        choice = res["choices"][0]
        msg = choice.get("message", {})
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning") or ""

        usage = res.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        header = (
            f"### 🌐 OpenRouter: `{model}`\n"
            f"*(Response in {latency:.2f}s • {prompt_tokens} in / {completion_tokens} out — total {total_tokens} tokens)*\n\n"
        )

        body = ""
        if reasoning and not content:
            body = f"> [!NOTE]\n> **Model Thought**:\n> {reasoning.strip()}\n"
        elif reasoning and content:
            body = f"<details><summary>Thought Process</summary>\n\n{reasoning.strip()}\n\n</details>\n\n{content}"
        else:
            body = content

        return header + body
    except Exception as e:
        return f"⚠️ Error parsing OpenRouter response: {e}\nRaw response:\n{json.dumps(res, indent=2)}"

# -------------------------------------------------------------
# Tool 6: openrouter_list_models
# -------------------------------------------------------------
def tool_openrouter_list_models(args):
    query = (args.get("query") or "").lower().strip()
    limit = min(int(args.get("limit", 20)), 100)

    url = "https://openrouter.ai/api/v1/models"
    headers = {"User-Agent": "Noha-AI-Assistant/1.0"}

    res = make_request(url, headers, method="GET", timeout=20)
    if "error" in res:
        return f"⚠️ Error fetching OpenRouter models: {res['error']}"

    models = res.get("data", [])
    if query:
        models = [
            m for m in models
            if query in m.get("id", "").lower()
            or query in m.get("name", "").lower()
            or query in m.get("description", "").lower()
        ]

    matched_count = len(models)
    models = models[:limit]

    output = [
        f"### 📋 OpenRouter Models ({matched_count} matches, showing top {len(models)}):",
        ""
    ]

    for m in models:
        mid = m.get("id")
        name = m.get("name", mid)
        ctx = m.get("context_length", "N/A")
        pricing = m.get("pricing", {})
        prompt_cost = float(pricing.get("prompt", 0)) * 1_000_000
        comp_cost = float(pricing.get("completion", 0)) * 1_000_000
        desc = (m.get("description") or "").replace("\n", " ").strip()
        if len(desc) > 110:
            desc = desc[:107] + "..."

        output.append(f"- **`{mid}`** ({name})")
        output.append(f"  - Context: {ctx} tokens | Price/1M: ${prompt_cost:.2f} in / ${comp_cost:.2f} out")
        if desc:
            output.append(f"  - *{desc}*")

    return "\n".join(output)

# -------------------------------------------------------------
# Tool 7: agentrouter_route_task
# -------------------------------------------------------------
def tool_agentrouter_route_task(args):
    task = args.get("task", "")
    category = args.get("category", "auto")
    preferred_provider = args.get("preferred_provider", "auto")
    api_key = args.get("api_key")

    ar_key = get_agentrouter_key(api_key)
    or_key = get_openrouter_key(api_key)
    groq_key = get_groq_key(api_key)

    if category == "auto":
        low = task.lower()
        if any(w in low for w in ["code", "function", "bug", "refactor", "api", "typescript", "python"]):
            category = "coding"
        elif any(w in low for w in ["proof", "math", "why", "logic", "algorithm", "complex", "reason"]):
            category = "reasoning"
        elif any(w in low for w in ["quick", "simple", "triage", "summary", "translate", "fast"]):
            category = "fast"
        elif any(w in low for w in ["critique", "review", "audit", "security"]):
            category = "review"
        else:
            category = "coding"

    # Route fast tasks to Groq for maximum speed if Groq key is present!
    if category == "fast" and groq_key:
        return tool_groq_chat({
            "model": "llama-3.1-8b-instant",
            "prompt": task,
            "system_prompt": "You are the Noha AI Fast Triage Specialist. Provide high-speed, direct, accurate responses without fluff."
        })

    # If AgentRouter key is present
    if ar_key and preferred_provider in ["agentrouter", "auto"]:
        url = "https://api.agentrouter.to/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {ar_key}",
            "Content-Type": "application/json",
            "User-Agent": "Noha-AI-Assistant/1.0"
        }
        payload = {
            "role": category,
            "messages": [{"role": "user", "content": task}]
        }
        res = make_request(url, headers, data=payload, method="POST", timeout=90)
        if "error" not in res:
            try:
                content = res["choices"][0]["message"]["content"]
                return f"### 🎯 AgentRouter Specialist (`{category}`)\n\n{content}"
            except Exception:
                pass

    # Fallback to OpenRouter mapping
    category_models = {
        "coding": "anthropic/claude-sonnet-5.5",
        "reasoning": "deepseek/deepseek-r1",
        "fast": "meta-llama/llama-3.3-70b-instruct",
        "creative": "anthropic/claude-sonnet-5.5",
        "review": "anthropic/claude-sonnet-5.5"
    }
    model = category_models.get(category, "anthropic/claude-sonnet-5.5")
    return tool_openrouter_chat({
        "model": model,
        "prompt": task,
        "system_prompt": f"You are a specialized agent in {category}. Deliver comprehensive expert solutions."
    })

# -------------------------------------------------------------
# Tool 8: noha_chat (Unified Active Model Chat)
# -------------------------------------------------------------
def tool_noha_chat(args):
    prompt = args.get("prompt")
    provider = (args.get("provider") or "").lower().strip()
    model = args.get("model")
    system_prompt = args.get("system_prompt")
    temperature = args.get("temperature", 0.7)
    max_tokens = args.get("max_tokens", 4096)

    state = load_active_state()
    active_prov = provider or state.get("provider", "groq")
    active_mod = model or state.get("model", "llama-3.3-70b-versatile")

    if active_prov == "groq":
        return tool_groq_chat({
            "model": active_mod,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
    elif active_prov == "openrouter":
        return tool_openrouter_chat({
            "model": active_mod,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
    elif active_prov == "agentrouter":
        return tool_agentrouter_route_task({
            "task": prompt,
            "category": active_mod
        })
    else:
        return f"⚠️ Unsupported provider: {active_prov}"

# -------------------------------------------------------------
# Tool 9: noha_compare_providers
# -------------------------------------------------------------
def tool_noha_compare_providers(args):
    prompt = args.get("prompt")
    system_prompt = args.get("system_prompt")
    
    if not prompt:
        return "⚠️ Error: 'prompt' is required for comparison."

    targets = [
        {"name": "⚡ Groq (Llama 3.3 70B)", "type": "groq", "model": "llama-3.3-70b-versatile"},
        {"name": "🧠 Groq (DeepSeek R1 Distill)", "type": "groq", "model": "deepseek-r1-distill-llama-70b"},
        {"name": "🌐 OpenRouter (Claude Sonnet 5.5)", "type": "openrouter", "model": "anthropic/claude-sonnet-5.5"},
    ]

    results = {}

    def run_target(t):
        if t["type"] == "groq":
            res = tool_groq_chat({
                "model": t["model"],
                "prompt": prompt,
                "system_prompt": system_prompt
            })
        else:
            res = tool_openrouter_chat({
                "model": t["model"],
                "prompt": prompt,
                "system_prompt": system_prompt
            })
        return t["name"], res

    with ThreadPoolExecutor(max_workers=len(targets)) as executor:
        future_map = {executor.submit(run_target, t): t for t in targets}
        for future in as_completed(future_map):
            name, output = future.result()
            results[name] = output

    lines = [f"# ⚖️ Noha AI Multi-Provider Benchmark\n**Prompt:** *{prompt}*\n"]
    for t in targets:
        name = t["name"]
        lines.append(f"## {name}")
        lines.append(results.get(name, "No response"))
        lines.append("\n---\n")

    return "\n".join(lines)

# -------------------------------------------------------------
# Tool 10: openrouter_compare_models
# -------------------------------------------------------------
def tool_openrouter_compare_models(args):
    models = args.get("models", [])
    prompt = args.get("prompt")
    system_prompt = args.get("system_prompt")

    if not models or not prompt:
        return "⚠️ Error: Both 'models' array and 'prompt' are required."

    models = models[:4]
    results = {}

    def fetch_single(mid):
        return mid, tool_openrouter_chat({
            "model": mid,
            "prompt": prompt,
            "system_prompt": system_prompt
        })

    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        future_map = {executor.submit(fetch_single, m): m for m in models}
        for future in as_completed(future_map):
            mid, resp = future.result()
            results[mid] = resp

    output = [f"# ⚖️ OpenRouter Model Comparison ({len(models)} models)\n"]
    for mid in models:
        output.append(f"## Model: `{mid}`")
        output.append(results.get(mid, "No response"))
        output.append("\n---\n")

    return "\n".join(output)

# -------------------------------------------------------------
# MCP Schema & Tool Definitions
# -------------------------------------------------------------
TOOLS = [
    {
        "name": "noha_status",
        "description": "Check Noha AI Assistant connectivity, API keys (Groq, OpenRouter, AgentRouter), and current active model selection.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "noha_switch_model",
        "description": "Switch the active provider and model in Noha AI Assistant (persists across sessions).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "description": "Provider to switch to: 'groq', 'openrouter', or 'agentrouter'.",
                    "enum": ["groq", "openrouter", "agentrouter"]
                },
                "model": {
                    "type": "string",
                    "description": "Model ID to activate (e.g. 'llama-3.3-70b-versatile', 'anthropic/claude-sonnet-5.5', or specialist role 'coding')."
                },
                "role": {
                    "type": "string",
                    "description": "Optional specialist role if provider is agentrouter."
                }
            },
            "required": ["provider"]
        }
    },
    {
        "name": "noha_chat",
        "description": "Execute a prompt using Noha AI Assistant's currently active model (supports Groq LPU, OpenRouter, and AgentRouter).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "User question or instruction."
                },
                "provider": {
                    "type": "string",
                    "description": "Optional provider override ('groq', 'openrouter', 'agentrouter')."
                },
                "model": {
                    "type": "string",
                    "description": "Optional model override."
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Optional system prompt instructions."
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature (0.0 to 1.0)."
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum completion tokens to generate."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "groq_chat",
        "description": "Ultra-fast chat completion using Groq LPU (~800 tokens/sec). Best for zero-latency responses, fast triage, and code generation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "User prompt."
                },
                "model": {
                    "type": "string",
                    "description": "Groq model (default: llama-3.3-70b-versatile, deepseek-r1-distill-llama-70b, llama-3.1-8b-instant, mixtral-8x7b-32768, gemma2-9b-it)."
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Optional system instruction."
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature (default 0.7)."
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens (default 4096)."
                },
                "api_key": {
                    "type": "string",
                    "description": "Optional explicit Groq API key."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "groq_list_models",
        "description": "List all active models available on Groq Cloud LPU.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "Optional explicit Groq API key."
                }
            }
        }
    },
    {
        "name": "openrouter_chat",
        "description": "Query frontier LLMs on OpenRouter (Claude 3.7 / Sonnet 5.5, DeepSeek R1, GPT-4o, o3-mini, Llama 3.3).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "OpenRouter model ID (e.g. anthropic/claude-sonnet-5.5, deepseek/deepseek-r1)."
                },
                "prompt": {
                    "type": "string",
                    "description": "The prompt or question."
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Optional system instructions."
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature (default 0.7)."
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens (default 4096)."
                },
                "api_key": {
                    "type": "string",
                    "description": "Optional explicit API key."
                }
            },
            "required": ["model", "prompt"]
        }
    },
    {
        "name": "openrouter_list_models",
        "description": "Search and list models from OpenRouter's 470+ catalog with real-time pricing and context windows.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (e.g. 'claude', 'deepseek', 'free', 'qwen')."
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 20, max 100)."
                }
            }
        }
    },
    {
        "name": "openrouter_compare_models",
        "description": "Run the same prompt across multiple OpenRouter models simultaneously to compare answers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "models": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of 2 to 4 OpenRouter model IDs."
                },
                "prompt": {
                    "type": "string",
                    "description": "Prompt to send to all models."
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Optional system instructions."
                }
            },
            "required": ["models", "prompt"]
        }
    },
    {
        "name": "agentrouter_route_task",
        "description": "Route a task to an autonomous specialist agent (coding, reasoning, fast triage, security review).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task description or code to process."
                },
                "category": {
                    "type": "string",
                    "description": "Role specialty ('auto', 'coding', 'reasoning', 'fast', 'review', 'creative').",
                    "default": "auto"
                },
                "preferred_provider": {
                    "type": "string",
                    "description": "Provider preference ('auto', 'agentrouter', 'groq', 'openrouter').",
                    "default": "auto"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "noha_compare_providers",
        "description": "Send a prompt concurrently to Groq LPU, DeepSeek R1, and OpenRouter Claude for a cross-provider speed and quality benchmark.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Prompt to benchmark across providers."
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Optional system prompt."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "noha_save_api_key",
        "description": "Save or update an API key for Groq, OpenRouter, or AgentRouter in Antigravity's .env configuration.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "description": "Provider name ('groq', 'openrouter', or 'agentrouter').",
                    "enum": ["groq", "openrouter", "agentrouter"]
                },
                "api_key": {
                    "type": "string",
                    "description": "API key string (e.g. 'gsk_...' or 'sk-or-v1-...')."
                }
            },
            "required": ["provider", "api_key"]
        }
    }
]

TOOL_HANDLERS = {
    "noha_status": tool_noha_status,
    "noha_switch_model": tool_noha_switch_model,
    "noha_save_api_key": tool_noha_save_api_key,
    "noha_chat": tool_noha_chat,
    "groq_chat": tool_groq_chat,
    "groq_list_models": tool_groq_list_models,
    "openrouter_chat": tool_openrouter_chat,
    "openrouter_list_models": tool_openrouter_list_models,
    "openrouter_compare_models": tool_openrouter_compare_models,
    "agentrouter_route_task": tool_agentrouter_route_task,
    "noha_compare_providers": tool_noha_compare_providers
}

def handle_jsonrpc(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "noha-ai-assistent",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found."
                }
            }

        try:
            result_text = handler(args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result_text)
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing tool '{tool_name}': {e}"
                        }
                    ]
                }
            }
    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not supported."
                }
            }
        return None

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_jsonrpc(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
