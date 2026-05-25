# paperchase (npx shim)

JS-world entry point for [PaperChase](https://paperchaselabs.com) — the proprietary AI operator CLI by PaperChaseLabs.

This package is a thin bootstrap: it ensures the `paperchase` Python package is installed via `pip --user`, then forwards your args to `python -m paperchase`.

## Usage

```bash
npx paperchase --help
```

On first run, this will:
1. Detect Python (`python3` or `python`, 3.11+ required)
2. Install the `paperchase` PyPI package via `pip install --user --upgrade paperchase`
3. Run `python -m paperchase <your args>`

## Why a shim?

The real core is Python. This package exists so JS-native consumers (Cursor, VS Code, Node-based agents) can drop into PaperChase without leaving their toolchain.

For native installs, see:

- `pip install paperchase` — Python users
- `brew install chasewebb/tap/paperchase` — Homebrew users
- The Rust `paperchase-fs-watcher` and TS `@paperchase/mcp` companions ship separately

## License

MIT
