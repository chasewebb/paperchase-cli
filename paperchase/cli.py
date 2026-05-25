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
    renderer.banner(animate=True)
    cfg, vault = _bootstrap()
    runtime_name = cfg.runtime_default
    if runtime_name not in registered_runtimes():
        console.print(f"[red]runtime '{runtime_name}' not available[/red]")
        return
    from paperchase.runtimes import get_runtime

    sess = ReplSession(runtime=get_runtime(runtime_name), vault=vault, workspace_root=cfg.workspace_root)
    sess.start()
    console.print("[dim]Type 'exit' or Ctrl-D to leave. Vault at ~/.paperchase/vault.db[/dim]\n")
    while True:
        try:
            text = console.input("[bright_green]> [/bright_green]")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if text.strip().lower() in {"exit", "quit"}:
            break
        if not text.strip():
            continue
        reply = sess.handle_user_input(text)
        renderer.print_assistant(reply)
    sess.stop()
    vault.close()
    renderer.sign_off()


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
