# meta-tools

MCP server for Claude Code that lets Claude detect gaps in its own toolset and build new tools to close them, live, in-session.

## Philosophy

The project is about **meta-tools**: tools whose subject matter is *other tools*. Rather than extending what an agent can do in a given domain, they extend how the agent relates to its own toolset — proposing new tools, building them, and (later) deciding which ones should be loaded at any moment. The toolset stops being a fixed input to the agent and becomes something the agent participates in shaping.

The motivating loop:

> Observe friction → Confirm gap with high confidence → Write the tool → Register it live → Use it now

Claude Code normally operates with a fixed toolset, so a gap (something that should be one tool call but isn't) leaves only workarounds — chains of `Bash` + `Read` + manual parsing. Meta-tools close that loop in-session.

The design constraint is **conservatism**. A false positive (building a tool that doesn't help, or duplicates an existing one) wastes time and pollutes the toolset. The bar is *"I am almost certain this tool would be used right now and multiple times in the future."* Default confidence threshold is `0.85`; a typical session should produce zero or one new tools, not five. This is a last-resort self-extension mechanism, not a brainstorming assistant.

The same philosophy generalises beyond creation: future meta-tools regulate the agent/toolset relation in other ways — retrieval (`find_and_load_tool`), eviction (`unload_tool`), pinning, usage tracking. See Phase 5 in `plan.txt`.

## Tools

The server exposes two MCP tools today:

- **`analyze_trajectory(goals, trajectory, available_tools)`** — Sends the trajectory to the analyzer model with a deliberately skeptical prompt. Returns `tool_needed: false` in the common case, or a structured `ToolSpec` (name, rationale, input schema, implementation approach) when confidence ≥ threshold.
- **`develop_tool(spec)`** — Generates a self-contained Python implementation for the spec, runs a safety gate (AST parse + dangerous-pattern scan), writes it to `generated_tools/<name>.py`, and live-registers it with FastMCP. Claude Code picks it up automatically via the `tools/list_changed` notification — no restart needed. Generated tools persist on disk and are reloaded on server startup.

The split into two calls is deliberate: Claude (or the user) can inspect the spec and abort before any code is written.

Planned (see `plan.txt`, Phase 5): a registry + bounded "tool shelf" with `find_and_load_tool` / `unload_tool`, so a large library of generated tools can be maintained without overwhelming Claude's context.

## Setup

```bash
pip install -e .
cp .env.example .env
# add your ANTHROPIC_API_KEY to .env
```

## Run smoke test

```bash
python examples/smoke_test.py positive   # expects tool_needed: true
python examples/smoke_test.py negative   # expects tool_needed: false
```

## Register with Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "meta-tools": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "meta_tools.server"],
      "cwd": "/path/to/meta-tools",
      "env": {
        "ANTHROPIC_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Usage

Call `analyze_trajectory` when you notice you are repeating the same multi-step workaround 3+ times:

```
analyze_trajectory(
  goals="what you are trying to accomplish",
  trajectory="the steps you have taken so far, including workarounds and failures",
  available_tools=["Bash", "Read", "Edit", ...]
)
```

Returns `tool_needed: false` in most cases. Returns a full tool spec only when confidence >= 0.85.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | Anthropic API key |
| `ANALYZER_MODEL` | `claude-sonnet-4-6` | Model for analysis |
| `CONFIDENCE_THRESHOLD` | `0.85` | Min confidence to return a positive result |
| `MAX_TOKENS` | `2048` | Max tokens for analyzer response |
