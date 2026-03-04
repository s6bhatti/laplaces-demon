---
name: termite
description: "Manages persistent tmux sessions for interactive CLI work (SSH, PDB, REPLs, long-running processes). Use when a command needs a real terminal, persistent state, or interactive input that the Bash tool cannot handle."
---

# termite

`termite` is a CLI tool installed globally on this system for managing tmux sessions on an isolated socket. Sessions persist across invocations and are invisible to the user's personal tmux.

## Commands

```
termite new <name>
termite kill <name>
termite list
termite run <session> <keys>... [--yield-time-ms N] [--tail-chars N]
termite send-file <session> <file>
termite read <session> [--tail-chars N]
termite export <session> <path>
```

## Key behavior

- `run` passes args directly to tmux `send-keys`. Quoted strings are literal text and unquoted words are tmux key names (e.g., `termite run s1 "ls -la" Enter`). When the value is already in an environment variable, pass it directly to `run` (e.g., `termite run s1 "$PASSWORD" Enter`).
- `run` without `--yield-time-ms` is fire-and-forget and returns no output.
- `run` with `--yield-time-ms` waits N milliseconds, then returns the visible pane contents. N must be under 1000, as this is only a quick check. For commands that need more time, use `sleep` and `termite read` to poll until completion.
- `read` returns the current visible pane contents (what a human would see on screen).
- `export` writes full scrollback history to a file.
- `--tail-chars` returns only the last N characters of output.
- Sessions use a 200x50 pane. Long lines are joined automatically on capture.

## Sending text with special characters

**Note**: This workaround is specific to Claude Code's Bash tool. Other agents (e.g., Codex) can use `send-file` but likely won't need to.

Claude Code's Bash tool (not the shell) escapes `!` to `\!` in the text it receives before passing it to the shell. This only affects text written directly in the command; an `!` inside an environment variable is unaffected, since the shell expands the variable after the escaping has already occurred. To work around this, use the Write tool to write the text to a temp file, then use `send-file`:

```bash
termite send-file session /tmp/.pw
termite run session Enter
rm /tmp/.pw
```
