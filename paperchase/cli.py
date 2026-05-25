"""PaperChase CLI — Click entry point."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from rich.console import Console

from paperchase import __version__
from paperchase.config import load_config
from paperchase.manifesto import BANNER
from paperchase.repl.session import ReplSession
from paperchase.runtimes import register, registered_runtimes
from paperchase.runtimes.ollama import OllamaRuntime
from paperchase.skills.registry import SkillRegistry
from paperchase.vault.store import VaultStore


console = Console()


def _vault_path() -> Path:
    return Path(os.environ.get("HOME", str(Path.home()))) / ".paperchase" / "vault.db"


def _bootstrap() -> tuple:
    cfg = load_config()
    vault = VaultStore(_vault_path())
    vault.connect()
    # Auto-register runtimes
    register(OllamaRuntime(host=cfg.ollama_host))
    # Future: detect API keys and register anthropic/openai
    return cfg, vault


@click.group(invoke_without_command=True, help="PaperChase — proprietary AI operator CLI by PaperChaseLabs.")
@click.version_option(__version__, prog_name="paperchase")
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)


@main.command(help="Open the interactive REPL.")
def chat() -> None:
    console.print(BANNER, style="bright_green")
    cfg, vault = _bootstrap()
    runtime_name = cfg.runtime_default
    if runtime_name not in registered_runtimes():
        console.print(f"[red]runtime '{runtime_name}' not available[/red]")
        return
    from paperchase.runtimes import get_runtime

    sess = ReplSession(runtime=get_runtime(runtime_name), vault=vault, workspace_root=cfg.workspace_root)
    sess.start()
    console.print("[dim]Type 'exit' or Ctrl-D to leave. Vault at ~/.paperchase/vault.db[/dim]")
    while True:
        try:
            text = console.input("[bright_green]> [/bright_green]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]exiting[/dim]")
            break
        if text.strip().lower() in {"exit", "quit"}:
            break
        if not text.strip():
            continue
        reply = sess.handle_user_input(text)
        console.print(reply)
    sess.stop()
    vault.close()


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
    execute = make_executor(shell_gate=gate, skill_registry=reg)
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
            console.print(f"[dim]ACT[/dim] {step.get('tool')} → {result.get('status', 'ok')}")
        elif state.phase == Phase.CRITIQUE:
            verdict_raw = do_critique(rt, state.goal, state.plan[state.cursor], state.last_result or {})
            verdict = Verdict(verdict_raw.get("verdict", "halt"))
            state.apply_verdict(verdict, reason=verdict_raw.get("reason", ""))
            vault.add_turn(sid, role="critic", content=verdict_raw)
            console.print(f"[dim]CRITIQUE[/dim] {verdict.value} · {verdict_raw.get('reason', '')[:80]}")
    vault.end_session(sid, status="done" if state.halt_reason == "DONE" else "halted")
    console.print(f"[bright_green]HALT[/bright_green] {state.halt_reason}")
    vault.close()


@main.command(help="Show registered runtimes and active configuration.")
def status() -> None:
    _, vault = _bootstrap()
    console.print(f"[bright_green]runtimes:[/bright_green] {', '.join(registered_runtimes()) or '(none)'}")
    console.print(f"[bright_green]vault:[/bright_green] {_vault_path()}")
    vault.close()


@main.command(help="Run as an MCP server.")
@click.option("--mcp-stdio", is_flag=True, help="MCP over stdio (default)")
def serve(mcp_stdio: bool) -> None:
    from paperchase.mcp.server import serve_stdio

    serve_stdio()


@main.group(help="Skill management.")
def skill() -> None:
    pass


@skill.command("install", help="Install a skill from a source (builtin:NAME | path | github:OWNER/REPO).")
@click.argument("source")
def skill_install(source: str) -> None:
    if not source.startswith("builtin:"):
        console.print("[yellow]only builtin: sources supported in v0.1[/yellow]")
        sys.exit(1)
    name = source.split(":", 1)[1]
    reg = SkillRegistry()
    reg.discover_builtin()
    try:
        m = reg.get(name)
        console.print(f"[bright_green]installed:[/bright_green] {m.name} v{m.version}")
    except KeyError:
        console.print(f"[red]no builtin skill named '{name}'[/red]")
        sys.exit(1)


@skill.command("list", help="List discovered skills.")
def skill_list() -> None:
    reg = SkillRegistry()
    reg.discover_builtin()
    for s in reg.list():
        console.print(f"  {s.name}  v{s.version}  — {s.description}")


if __name__ == "__main__":
    main()
