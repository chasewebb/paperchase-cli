# paperchase-fs-watcher

Rust file system watcher for [PaperChase](https://paperchaselabs.com).

Streams `notify` events (create / modify / remove) over a Unix socket to the Python core.

## Why Rust?

- `notify` is the gold-standard cross-platform fs-watch library (kqueue on macOS, inotify on Linux, ReadDirectoryChangesW on Windows).
- Zero-GC. Long-running. Tiny static binary.
- Python's `watchdog` has the same backends but slower event throughput and higher latency under burst load. For agent workflows that respond to large vault changes, the Rust path keeps you under 50ms per event.

## Build

```bash
cargo build --release
ls -la target/release/paperchase-fs-watcher
```

## Run

```bash
paperchase-fs-watcher /path/to/watch
# or with a custom socket:
paperchase-fs-watcher /path/to/watch --socket /tmp/my.sock
```

Default socket: `~/.paperchase/watcher.sock`.

## Wire format

Newline-delimited JSON per event:

```json
{"kind": "modify", "path": "/abs/path/to/file"}
```

`kind` is one of: `create`, `modify`, `remove`, `other`.

## License

MIT
