"""First-run ASCII codec banner — MGS codec aesthetic for the REPL boot.

Rendered by paperchase/repl/renderer.py:banner() in phosphor green.
"""
from __future__ import annotations

from paperchase import __version__


BANNER = rf"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗  █████╗ ██████╗ ███████╗██████╗  ██████╗██╗  ██╗       ║
║   ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║       ║
║   ██████╔╝███████║██████╔╝█████╗  ██████╔╝██║     ███████║       ║
║   ██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗██║     ██╔══██║       ║
║   ██║     ██║  ██║██║     ███████╗██║  ██║╚██████╗██║  ██║       ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝       ║
║                       A S E                                      ║
║   ────────────────────────────────────────────────────────       ║
║                                                                  ║
║   [ TRANSMISSION SIGNED BY PAPERCHASELABS ]                      ║
║   v{__version__:<8} · FREQ 140.85 · CH 401 · CLI                      ║
║                                                                  ║
║   ↗ paperchaselabs.com                                           ║
║   ↗ github.com/chasewebb/paperchase-cli                          ║
║                                                                  ║
║   The Sovereign Operator System.                                 ║
║   Built around the operator, not the platform.                   ║
║   Self-hosted · Operator-owned · MIT                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""


BOOT_STATUS = [
    "[ NODE SYNC ESTABLISHED ]",
    "[ MEMORY ENGINE ONLINE ]",
    "[ AUTONOMOUS AGENTS ACTIVE ]",
]


SIGN_OFF = "[ TRANSMISSION COMPLETE · FREQ 140.85 ]"
