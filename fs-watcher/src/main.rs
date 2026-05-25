// fs-watcher/src/main.rs
use anyhow::Result;
use clap::Parser;
use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use serde::Serialize;
use std::io::Write;
use std::os::unix::net::UnixStream;
use std::path::PathBuf;
use std::sync::mpsc::channel;
use std::time::Duration;

#[derive(Parser, Debug)]
#[command(name = "paperchase-fs-watcher", version, about)]
struct Cli {
    /// Directory to watch recursively
    path: PathBuf,
    /// Unix socket where events get emitted (default ~/.paperchase/watcher.sock)
    #[arg(long)]
    socket: Option<PathBuf>,
}

#[derive(Serialize)]
struct WatchEvent {
    kind: String,
    path: String,
}

fn classify(kind: &EventKind) -> &'static str {
    match kind {
        EventKind::Create(_) => "create",
        EventKind::Modify(_) => "modify",
        EventKind::Remove(_) => "remove",
        _ => "other",
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let socket_path = cli.socket.unwrap_or_else(|| {
        let mut p = dirs_home().expect("HOME not set");
        p.push(".paperchase");
        p.push("watcher.sock");
        p
    });

    let (tx, rx) = channel::<notify::Result<Event>>();
    let mut watcher: RecommendedWatcher = Watcher::new(
        move |res| { let _ = tx.send(res); },
        Config::default().with_poll_interval(Duration::from_secs(2)),
    )?;
    watcher.watch(&cli.path, RecursiveMode::Recursive)?;

    eprintln!(
        "paperchase-fs-watcher: watching {} → emitting to {}",
        cli.path.display(),
        socket_path.display()
    );

    loop {
        let evt = match rx.recv() {
            Ok(Ok(e)) => e,
            Ok(Err(_)) => continue,
            Err(_) => break,
        };
        let kind = classify(&evt.kind);
        for path in evt.paths {
            let payload = WatchEvent { kind: kind.into(), path: path.display().to_string() };
            if let Ok(mut sock) = UnixStream::connect(&socket_path) {
                let line = serde_json::to_string(&payload)? + "\n";
                let _ = sock.write_all(line.as_bytes());
            }
        }
    }
    Ok(())
}

fn dirs_home() -> Option<PathBuf> {
    std::env::var_os("HOME").map(PathBuf::from)
}
