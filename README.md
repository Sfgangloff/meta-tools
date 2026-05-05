# meta-tools

MCP server for Claude Code that analyzes reasoning trajectories to detect missing tools.

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
