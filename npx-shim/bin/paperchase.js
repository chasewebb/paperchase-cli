#!/usr/bin/env node
/**
 * paperchase npx shim — ensures Python paperchase is installed, then forwards args.
 */
const { spawnSync } = require("node:child_process");
const { existsSync } = require("node:fs");

function tryRun(cmd, args) {
  const r = spawnSync(cmd, args, { stdio: "inherit" });
  return r.status;
}

function pythonAvailable() {
  for (const py of ["python3", "python"]) {
    const r = spawnSync(py, ["--version"], { stdio: "ignore" });
    if (r.status === 0) return py;
  }
  return null;
}

function ensurePaperchaseInstalled(py) {
  const r = spawnSync(py, ["-c", "import paperchase"], { stdio: "ignore" });
  if (r.status === 0) return true;
  console.error("[paperchase] installing python package via pip --user…");
  const install = spawnSync(py, ["-m", "pip", "install", "--user", "--upgrade", "paperchase"], { stdio: "inherit" });
  return install.status === 0;
}

function main() {
  const args = process.argv.slice(2);
  const py = pythonAvailable();
  if (!py) {
    console.error("[paperchase] no python found. Install Python 3.11+ first.");
    process.exit(1);
  }
  if (!ensurePaperchaseInstalled(py)) {
    console.error("[paperchase] pip install failed. Try: pipx install paperchase");
    process.exit(1);
  }
  const code = tryRun(py, ["-m", "paperchase", ...args]);
  process.exit(code ?? 0);
}

main();
