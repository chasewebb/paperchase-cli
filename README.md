<p align="center">
  <img src="art/operator-hud.png" alt="PaperChase Operator — Sovereign Operator System" width="640" />
</p>

<p align="center">
  <strong>[ TRANSMISSION SIGNED BY PAPERCHASELABS ]</strong><br/>
  <code>FREQ 140.85 · CH 401 · CLI</code><br/>
  <a href="https://paperchaselabs.com">paperchaselabs.com</a>
</p>

<p align="center">
  <img src="art/operator.png" alt="PaperChase — official operator logo" width="120" />
</p>

# PaperChase

> **The Sovereign Operator System.** Autonomous AI operator CLI — Claude-Code-style REPL meets Hermes-class autonomous loop. Memory engine, multi-agent dispatch, MCP server, skill registry. Operator-owned. Sovereign by default. MIT.
>
> _Follow the white rabbit._

```bash
pip install paperchase
paperchase
```

Built by [PaperChaseLabs](https://paperchaselabs.com).

---

## Install

```bash
# canonical
pip install paperchase

# zero-install one-shot
uvx paperchase

# js world
npx paperchase

# macOS one-line
brew install chasewebb/paperchase/paperchase
```

## Quickstart

```bash
# Interactive REPL with Ollama (free, local). Codec banner on boot.
paperchase chat

# Autonomous loop — PLAN → ACT → CRITIQUE, with subagent fan-out
paperchase auto "summarize the readme of https://github.com/openai/openai-python"

# Run as an MCP server (Claude Desktop, Cursor, any MCP client)
paperchase serve --mcp-stdio

# Install skills — three sources supported
paperchase skill install builtin:web-research
paperchase skill install github:operator/some-skill
paperchase skill install ./my-local-skill

# Reflect on recent sessions — writes ~/.paperchase/learnings.md
# The operator persona auto-loads it on every future session
paperchase reflect

# Runtimes, vault, skills, lab links
paperchase status
```

## Why PaperChase

|  | Claude Code | Cursor | Hermes Agent | **PaperChase** |
|---|---|---|---|---|
| License | Closed | Closed | OSS | **MIT** |
| Local-first | No | No | Partial | **Yes (Ollama default)** |
| Autonomous loop | No | Limited | Yes | **Yes** |
| **Multi-agent dispatch** | No | No | Yes | **Yes (`SpawnAgent` tool)** |
| **Self-augmenting memory** | No | No | Some | **Yes (`paperchase reflect`)** |
| **MCP server out-of-the-box** | No | No | No | **Yes** |
| **Telemetry / data collection** | Yes | Yes | Minimal | **Zero** |
| Polyglot install | npm only | App only | pip only | **pip + uvx + npx + brew** |

The only autonomous operator CLI that's MIT, local-first, ships an MCP server, and supports every package manager you already use.

## What's in v0.1

- **Interactive REPL** with codec UI (MGS1 codec aesthetic, animated boot)
- **Autonomous loop** — PLAN/ACT/CRITIQUE state machine with halt conditions
- **`SpawnAgent` tool** — child loops for parallel work, budget-guarded
- **9 tools**: Read · Write · Edit · Glob · Grep · gated Bash · WebFetch (HTTPS only) · Skills · SpawnAgent
- **Skill registry**: install from `builtin:`, local path, or `github:owner/repo[@ref]`
- **Self-reflection**: `paperchase reflect` reads vault, distills patterns, writes `~/.paperchase/learnings.md` — auto-loaded into the persona prompt every future session
- **Vault**: SQLite at `~/.paperchase/vault.db`, every session/turn/tool-call recorded, sessions resumable
- **3 runtimes**: Ollama (default, local, free), Anthropic (opt-in via env), OpenAI (opt-in via env)
- **MCP server**: stdio + HTTP transports, exports all 9 tools
- **Polyglot install**: pip · uvx · npx · brew

## Skills

PaperChase ships with one reference skill (`web-research`). Skills are pluggable abilities the agent can absorb and switch between like modes. Install from anywhere:

```bash
paperchase skill install builtin:web-research
paperchase skill install github:owner/repo
paperchase skill install ./my-local-skill
```

Each skill is a directory with a `skill.toml` manifest + a Python entry point. See [docs/SKILLS.md](docs/SKILLS.md).

## MCP integration

Drop this into `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paperchase": {
      "command": "paperchase",
      "args": ["serve", "--mcp-stdio"]
    }
  }
}
```

## Privacy

**Zero telemetry. Zero data collection.** No usage pings, no error reports, no metrics shipped anywhere. Your vault is a local SQLite file. Ollama runs on your machine. Anthropic/OpenAI runtimes are opt-in via env vars — your keys, your bill, your data. WebFetch goes only where the operator (or agent) points it. Skills installed from GitHub clone over public HTTPS, no auth.

The only network call PaperChase initiates without you asking is the runtime call to Ollama at `localhost:11434`. That's it.

## Roadmap → v0.2

- Skill marketplace (curated registry + UI)
- Voice in/out (Whisper input + Grok voice output)
- Channel adapters: Telegram, Discord, Slack — agent reachable from anywhere
- Self-fine-tune loop (capture preferred trajectories, fine-tune nightly)
- Embeddings-based vault retrieval (v0.1 uses FTS5)

## Links

- Lab — https://paperchaselabs.com
- Discord — https://discord.gg/5vYFCcKVrB
- Substack — https://substack.com/@paperchase
- Book a call — https://calendly.com/paperchasewebb/15min

---

<p align="center">
  <img src="art/coin.webp" alt="" width="80" />
</p>

<p align="center">
  <sub>PAPERCHASEWEBB INC. · BUILT IN HONOLULU · 2018→</sub>
</p>
