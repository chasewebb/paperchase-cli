"""PaperChase CLI — Click entry point.

The user-facing surface. Wires the renderer (codec UI), config, vault, runtimes,
skills, REPL, autonomous loop, MCP server, and reflection together.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from rich.console import Console

from paperchase import __version__
from paperchase.config import load_config
from paperchase.repl import renderer
from paperchase.repl.session import ReplSession
from paperchase.runtimes import register, registered_runtimes
from paperchase.runtimes.ollama import OllamaRuntime
from paperchase.skills.registry import SkillRegistry
from paperchase.vault.store import VaultStore


console = Console()


def _home() -> Path:
    return Path(os.environ.get("HOME", str(Path.home())))


def _vault_path() -> Path:
    return _home() / ".paperchase" / "vault.db"


def _bootstrap() -> tuple:
    cfg = load_config()
    vault = VaultStore(_vault_path())
    vault.connect()
    register(OllamaRuntime(host=cfg.ollama_host))
    # Future: detect ANTHROPIC_API_KEY / OPENAI_API_KEY and register those
    return cfg, vault


@click.group(
    invoke_without_command=True,
    help="PaperChase — the Sovereign Operator System. Autonomous AI operator CLI by PaperChaseLabs.",
)
@click.version_option(
    __version__,
    prog_name="paperchase",
    message="paperchase %(version)s · paperchaselabs.com · github.com/chasewebb/paperchase-cli",
)
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)


@main.command(help="Open the interactive REPL.")
def chat() -> None:
    import os as _os
    import shlex as _shlex
    import subprocess as _subprocess

    cfg, vault = _bootstrap()
    runtime_name = cfg.runtime_default
    reg = SkillRegistry()
    reg.discover_builtin()

    renderer.banner(
        animate=True,
        model=runtime_name,
        tool_count=9,
        active_runtimes=len(registered_runtimes()),
        total_runtimes=3,
        skill_count=len(reg.list()),
    )

    if runtime_name not in registered_runtimes():
        renderer.alert(f"runtime '{runtime_name}' not available")
        return
    from paperchase.runtimes import get_runtime

    sess = ReplSession(runtime=get_runtime(runtime_name), vault=vault, workspace_root=cfg.workspace_root)
    sess.start()

    state: dict = {
        "backend": runtime_name,
        "last_user": None,
        "last_assistant": None,
        "last_model": runtime_name,
        "tokens_total": 0,
        "plan_mode": False,
        "attachments": [],
        "turn_count": 0,
    }

    while True:
        try:
            prompt_prefix = "[bright_green]" + ("[PLAN] " if state["plan_mode"] else "") + "> [/bright_green]"
            text = console.input(prompt_prefix)
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        stripped = text.strip()
        if not stripped:
            continue
        # Slash commands
        if stripped.startswith("/"):
            parts = stripped[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""
            if cmd in {"quit", "exit", "q"}:
                break
            if cmd == "help":
                renderer.slash_help()
                continue
            if cmd == "clear":
                console.clear()
                continue
            if cmd == "reset":
                sess.stop()
                sess = ReplSession(runtime=sess.runtime, vault=vault, workspace_root=cfg.workspace_root)
                sess.start()
                state["last_user"] = state["last_assistant"] = None
                state["attachments"] = []
                renderer.print_meta("  conversation memory cleared")
                continue
            if cmd == "retry":
                if not state["last_user"]:
                    renderer.alert("nothing to retry — no previous turn")
                    continue
                _handle_chat_turn(state["last_user"], state, sess, reg)
                continue
            if cmd == "undo":
                if len(sess.history) >= 2:
                    sess.history.pop()
                    sess.history.pop()
                    renderer.print_meta("  last turn pair dropped")
                else:
                    renderer.alert("nothing to undo")
                continue
            if cmd == "last":
                if state["last_assistant"]:
                    renderer.print_assistant(state["last_assistant"])
                else:
                    renderer.print_meta("  no assistant response yet")
                continue
            if cmd == "tokens":
                console.print(f"  [bright_green]tokens this session:[/bright_green] {state['tokens_total']:,}")
                continue
            if cmd == "model":
                if rest:
                    state["last_model"] = rest.strip()
                    renderer.print_meta(f"  next turn will request model: {state['last_model']}")
                else:
                    console.print(f"  [bright_green]model:[/bright_green] {state['last_model']}")
                continue
            if cmd == "backend":
                if rest:
                    if rest.strip() in registered_runtimes():
                        state["backend"] = rest.strip()
                        sess.runtime = get_runtime(state["backend"])
                        renderer.print_meta(f"  backend → {state['backend']}")
                    else:
                        renderer.alert(f"unknown backend '{rest.strip()}' (try /backends)")
                else:
                    console.print(f"  [bright_green]backend:[/bright_green] {state['backend']}")
                continue
            if cmd == "backends":
                for name in registered_runtimes():
                    mark = "●" if name == state["backend"] else "○"
                    console.print(f"  [bright_green]{mark}[/bright_green] {name}")
                continue
            if cmd == "plan":
                state["plan_mode"] = not state["plan_mode"]
                renderer.print_meta(
                    f"  plan mode {'ON — analysis only, no edits' if state['plan_mode'] else 'OFF'}"
                )
                continue
            if cmd == "read":
                if not rest:
                    renderer.alert("usage: /read PATH")
                    continue
                try:
                    body = Path(rest.strip()).read_text()
                    state["attachments"].append({"kind": "file", "path": rest.strip(), "body": body})
                    renderer.print_meta(f"  attached {len(body)} chars from {rest.strip()}")
                except OSError as e:
                    renderer.alert(f"read failed: {e}")
                continue
            if cmd == "bash":
                if not rest:
                    renderer.alert("usage: /bash COMMAND")
                    continue
                try:
                    r = _subprocess.run(rest, shell=True, capture_output=True, text=True, timeout=30)
                    out = (r.stdout or "") + (r.stderr or "")
                    console.print(out[:2000] or "(no output)")
                    state["attachments"].append({"kind": "shell", "cmd": rest, "output": out[:4000]})
                except _subprocess.TimeoutExpired:
                    renderer.alert("bash command timed out (30s)")
                continue
            if cmd == "attach":
                if not state["attachments"]:
                    renderer.print_meta("  no attachments queued")
                else:
                    for i, a in enumerate(state["attachments"], 1):
                        console.print(f"  [{i}] {a['kind']} · {a.get('path', a.get('cmd', ''))[:60]}")
                continue
            if cmd == "save":
                if not state["last_assistant"]:
                    renderer.alert("nothing to save — no assistant response yet")
                    continue
                path = rest.strip() or f"paperchase-{int(__import__('time').time())}.md"
                Path(path).write_text(state["last_assistant"])
                renderer.print_meta(f"  saved last response → {path}")
                continue
            if cmd == "copy":
                if not state["last_assistant"]:
                    renderer.alert("nothing to copy — no assistant response yet")
                    continue
                try:
                    p = _subprocess.Popen(["pbcopy"], stdin=_subprocess.PIPE)
                    p.communicate(state["last_assistant"].encode())
                    renderer.print_meta("  copied last response to clipboard")
                except FileNotFoundError:
                    renderer.alert("pbcopy not available (macOS only)")
                continue
            if cmd == "status":
                _print_status_inline(cfg, vault, reg)
                continue
            if cmd == "skills":
                for s in reg.list():
                    console.print(f"  [bright_green]{s.name}[/bright_green]  v{s.version}  — {s.description[:80]}")
                if not reg.list():
                    renderer.print_meta("  no skills installed")
                continue
            if cmd == "reflect":
                _run_reflect_inline(cfg, vault)
                continue
            renderer.alert(f"unknown slash command: /{cmd}  (try /help)")
            continue

        # Normal chat turn
        _handle_chat_turn(text, state, sess, reg)
    sess.stop()
    vault.close()
    renderer.sign_off(state["turn_count"])


def _handle_chat_turn(text: str, state: dict, sess, reg) -> None:
    """Process one user turn — handles attachments + plan mode + token tracking."""
    # Prepend any queued attachments
    if state["attachments"]:
        attachment_blocks = []
        for a in state["attachments"]:
            if a["kind"] == "file":
                attachment_blocks.append(f"[file:{a['path']}]\n{a['body']}\n[/file]")
            elif a["kind"] == "shell":
                attachment_blocks.append(f"[shell:{a['cmd']}]\n{a['output']}\n[/shell]")
        text = "\n\n".join(attachment_blocks) + "\n\n" + text
        state["attachments"] = []
    if state["plan_mode"]:
        text = (
            "PLAN MODE — analyze only, do not propose edits or actions. "
            "Output a numbered plan of what you'd do.\n\n" + text
        )
    state["last_user"] = text
    reply = sess.handle_user_input(text)
    state["last_assistant"] = reply
    # Token tracking — pull from runtime's last response if available
    last_response = getattr(sess.runtime, "last_response", None)
    if last_response and getattr(last_response, "raw", None):
        raw = last_response.raw
        n = (
            raw.get("eval_count")  # Ollama
            or (raw.get("usage") or {}).get("total_tokens")  # OpenAI/Anthropic-shape
            or 0
        )
        state["tokens_total"] += n
    renderer.print_assistant(reply)
    state["turn_count"] += 1


def _print_status_inline(cfg, vault, reg) -> None:
    renderer.print_section(
        "RUNTIME",
        [
            ("registered", ", ".join(registered_runtimes()) or "(none)"),
            ("default", cfg.runtime_default),
            ("ollama host", cfg.ollama_host),
        ],
    )
    renderer.print_section(
        "VAULT",
        [
            ("path", str(_vault_path())),
            ("workspace", str(cfg.workspace_root)),
            ("max iters", str(cfg.max_iterations)),
        ],
    )
    skill_rows = [(s.name, f"v{s.version}") for s in reg.list()]
    renderer.print_section("SKILLS", skill_rows or [("(none)", "")])
    console.print()
    console.print("[bright_green][ LINKS ][/bright_green]")
    renderer.print_links()


def _run_reflect_inline(cfg, vault) -> None:
    from paperchase.runtimes import get_runtime
    from paperchase.runtimes.base import Message
    from paperchase.vault.retriever import get_recent_sessions_summary, save_learnings

    summary_md = get_recent_sessions_summary(vault, limit=10)
    if summary_md.strip() == "_no sessions yet_":
        renderer.print_meta("  no sessions in vault yet — nothing to reflect on")
        return
    rt = get_runtime(cfg.runtime_default)
    msgs = [
        Message(
            role="system",
            content=(
                "You are PaperChase's reflection module. Given a markdown summary of recent "
                "agent sessions, identify recurring patterns, failure modes, and successful "
                "approaches. Output a concise markdown memo (max 1500 chars) for future "
                "agent sessions to internalize. No preamble — just the memo."
            ),
        ),
        Message(role="user", content=summary_md),
    ]
    response = rt.chat(msgs)
    memo = response.content.strip()[:1500]
    save_learnings(_home(), memo)
    console.print("[bright_green][ LEARNINGS WRITTEN ][/bright_green] ~/.paperchase/learnings.md")
    console.print()
    console.print(memo)


@main.command(name="auto", help="Run the autonomous PLAN/ACT/CRITIQUE loop until done.")
@click.argument("goal", nargs=-1, required=True)
@click.option("--max-iterations", type=int, default=None)
def auto_cmd(goal: tuple, max_iterations: int | None) -> None:
    from paperchase.loop.executor import make_executor
    from paperchase.loop.planner import plan as do_plan
    from paperchase.loop.critic import critique as do_critique
    from paperchase.loop.state import LoopState, Phase, Verdict
    from paperchase.runtimes import get_runtime
    from paperchase.tools.shell import ShellGate

    goal_text = " ".join(goal)
    cfg, vault = _bootstrap()
    rt = get_runtime(cfg.runtime_default)
    reg = SkillRegistry()
    reg.discover_builtin()
    gate = ShellGate(auto_allow_patterns=[], interactive=False)
    # Pass runtime into the executor so SpawnAgent can dispatch subagents
    execute = make_executor(shell_gate=gate, skill_registry=reg, runtime=rt)
    state = LoopState(
        goal=goal_text,
        max_iterations=max_iterations or cfg.max_iterations,
    )
    sid = vault.create_session(mode="auto", goal=goal_text)
    console.print(f"[bright_green]GOAL:[/bright_green] {goal_text}")
    while not state.halted:
        if state.phase == Phase.PLAN:
            try:
                steps = do_plan(rt, state.goal, tools=[], context="")
                state.set_plan(steps)
                vault.add_turn(sid, role="planner", content={"steps": steps})
                console.print(f"[dim]PLAN[/dim] {len(steps)} step(s)")
            except ValueError as e:
                state.record_planner_failure()
                vault.add_turn(sid, role="planner", content={"error": str(e)})
        elif state.phase == Phase.ACT:
            step = state.plan[state.cursor]
            result = execute(step)
            state.record_step_result(result)
            vault.add_turn(sid, role="executor", content={"step": step, "result": result})
            console.print(f"[dim]ACT[/dim] {step.get('tool')} -> {result.get('status', 'ok')}")
        elif state.phase == Phase.CRITIQUE:
            verdict_raw = do_critique(rt, state.goal, state.plan[state.cursor], state.last_result or {})
            verdict = Verdict(verdict_raw.get("verdict", "halt"))
            state.apply_verdict(verdict, reason=verdict_raw.get("reason", ""))
            vault.add_turn(sid, role="critic", content=verdict_raw)
            console.print(f"[dim]CRITIQUE[/dim] {verdict.value} · {verdict_raw.get('reason', '')[:80]}")
    vault.end_session(sid, status="done" if state.halt_reason == "DONE" else "halted")
    console.print(f"[bright_green]HALT[/bright_green] {state.halt_reason}")
    vault.close()


@main.command(help="Show registered runtimes, vault path, and lab links.")
def status() -> None:
    cfg, vault = _bootstrap()
    renderer.print_section(
        "RUNTIME",
        [
            ("registered", ", ".join(registered_runtimes()) or "(none)"),
            ("default", cfg.runtime_default),
            ("ollama host", cfg.ollama_host),
        ],
    )
    renderer.print_section(
        "VAULT",
        [
            ("path", str(_vault_path())),
            ("workspace", str(cfg.workspace_root)),
            ("max iters", str(cfg.max_iterations)),
        ],
    )
    reg = SkillRegistry()
    reg.discover_builtin()
    skill_rows = [(s.name, f"v{s.version}") for s in reg.list()]
    renderer.print_section("SKILLS", skill_rows or [("(none)", "")])
    console.print()
    console.print("[bright_green][ LINKS ][/bright_green]")
    renderer.print_links()
    vault.close()


@main.command(help="Read recent vault sessions, distill patterns into ~/.paperchase/learnings.md.")
@click.option("--limit", type=int, default=10, help="Recent sessions to read")
@click.option("--print/--no-print", "do_print", default=True, help="Print the memo after writing it")
def reflect(limit: int, do_print: bool) -> None:
    from paperchase.runtimes import get_runtime
    from paperchase.runtimes.base import Message
    from paperchase.vault.retriever import get_recent_sessions_summary, save_learnings

    cfg, vault = _bootstrap()
    summary_md = get_recent_sessions_summary(vault, limit=limit)
    vault.close()
    if summary_md.strip() == "_no sessions yet_":
        console.print("[dim]no sessions in vault yet — nothing to reflect on[/dim]")
        return

    rt = get_runtime(cfg.runtime_default)
    msgs = [
        Message(
            role="system",
            content=(
                "You are PaperChase's reflection module. Given a markdown summary of recent "
                "agent sessions, identify recurring patterns, failure modes, and successful "
                "approaches. Output a concise markdown memo (max 1500 chars) that future "
                "agent sessions should internalize. No preamble, no postscript — just the memo."
            ),
        ),
        Message(role="user", content=summary_md),
    ]
    response = rt.chat(msgs)
    memo = response.content.strip()[:1500]
    save_learnings(_home(), memo)
    console.print("[bright_green][ LEARNINGS WRITTEN ][/bright_green] ~/.paperchase/learnings.md")
    if do_print:
        console.print()
        console.print(memo)


@main.command(help="Run as an MCP server.")
@click.option("--mcp-stdio", is_flag=True, help="MCP over stdio (default)")
def serve(mcp_stdio: bool) -> None:
    from paperchase.mcp.server import serve_stdio

    serve_stdio()


@main.group(help="Skill management.")
def skill() -> None:
    pass


@skill.command(
    "install",
    help="Install a skill from a source: builtin:NAME, github:OWNER/REPO[@REF], or local path.",
)
@click.argument("source")
def skill_install(source: str) -> None:
    reg = SkillRegistry()
    reg.discover_builtin()
    if source.startswith("builtin:"):
        name = source.split(":", 1)[1]
        try:
            m = reg.get(name)
            console.print(f"[bright_green]installed:[/bright_green] {m.name} v{m.version}")
        except KeyError:
            console.print(f"[red]no builtin skill named '{name}'[/red]")
            sys.exit(1)
        return
    if source.startswith("github:"):
        try:
            m = reg.discover_github(source)
            console.print(f"[bright_green]installed:[/bright_green] {m.name} v{m.version} (from {source})")
        except Exception as e:
            console.print(f"[red]github install failed:[/red] {e}")
            sys.exit(1)
        return
    # Local path
    p = Path(source)
    if p.exists() and p.is_dir():
        try:
            reg.discover_local(p)
            m = reg.list()[-1]
            console.print(f"[bright_green]installed:[/bright_green] {m.name} v{m.version} (from {p})")
        except Exception as e:
            console.print(f"[red]local install failed:[/red] {e}")
            sys.exit(1)
        return
    console.print(
        f"[red]unknown source '{source}'.[/red] Use builtin:NAME, github:OWNER/REPO, or a local path."
    )
    sys.exit(1)


@skill.command("list", help="List discovered skills.")
def skill_list() -> None:
    reg = SkillRegistry()
    reg.discover_builtin()
    for s in reg.list():
        console.print(f"  {s.name}  v{s.version}  — {s.description}")


if __name__ == "__main__":
    main()
