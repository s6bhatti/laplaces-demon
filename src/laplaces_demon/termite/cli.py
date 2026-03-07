import click

from laplaces_demon.termite.core import (
    SessionExistsError,
    SessionNotFoundError,
    TermiteManager,
)


@click.group()
def cli() -> None:
    """Termite: tmux session manager for AI agents."""


@cli.command()
@click.argument("name")
def new(name: str) -> None:
    """Create a new termite session."""
    manager = TermiteManager()
    try:
        manager.new_session(name=name)
    except SessionExistsError as e:
        raise click.ClickException(str(e))
    click.echo(f"Created session '{name}'")


@cli.command()
@click.argument("name")
def kill(name: str) -> None:
    """Kill a termite session."""
    manager = TermiteManager()
    try:
        manager.kill_session(name=name)
    except SessionNotFoundError as e:
        raise click.ClickException(str(e))
    click.echo(f"Killed session '{name}'")


@cli.command("list")
def list_sessions() -> None:
    """List all termite sessions."""
    manager = TermiteManager()
    sessions = manager.list_sessions()
    if not sessions:
        click.echo("No sessions")
        return
    for name in sessions:
        click.echo(name)


@cli.command()
@click.argument("session")
@click.argument("keys", nargs=-1, required=True)
@click.option(
    "--yield-time-ms",
    type=int,
    default=None,
    help="Wait duration before capturing output",
)
@click.option(
    "--tail-chars", type=int, default=None, help="Return last N characters of output"
)
def run(
    session: str,
    keys: tuple[str, ...],
    yield_time_ms: int | None,
    tail_chars: int | None,
) -> None:
    """Send keys to a termite session. Quoted strings are literal text, unquoted words are tmux key names."""
    manager = TermiteManager()
    try:
        output = manager.run_command(
            session_name=session,
            keys=keys,
            yield_time_ms=yield_time_ms,
            tail_chars=tail_chars,
        )
    except SessionNotFoundError as e:
        raise click.ClickException(str(e))
    if output is not None:
        click.echo(output)


@cli.command()
@click.argument("session")
@click.option(
    "--tail-chars", type=int, default=None, help="Return last N characters of output"
)
def read(session: str, tail_chars: int | None) -> None:
    """Read the current visible pane contents."""
    manager = TermiteManager()
    try:
        output = manager.read_pane(session_name=session, tail_chars=tail_chars)
    except SessionNotFoundError as e:
        raise click.ClickException(str(e))
    click.echo(output)


@cli.command()
@click.argument("session")
@click.option(
    "--timeout-s",
    type=int,
    required=True,
    help="Maximum time in seconds to wait for the pane to change",
)
def wait(session: str, timeout_s: int) -> None:
    """Wait until the visible pane contents change and print them."""
    manager = TermiteManager()
    try:
        output = manager.wait_for_change(
            session_name=session,
            timeout_s=timeout_s,
        )
    except SessionNotFoundError as e:
        raise click.ClickException(str(e))
    if output is not None:
        click.echo(output)
        return
    click.echo("Timed out waiting for pane change")


@cli.command("send-file")
@click.argument("session")
@click.argument("file", type=click.Path(exists=True))
def send_file(session: str, file: str) -> None:
    """Send file contents as literal text to a session."""
    manager = TermiteManager()
    try:
        manager.send_file(session_name=session, file_path=file)
    except SessionNotFoundError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("session")
@click.argument("path", type=click.Path())
def export(session: str, path: str) -> None:
    """Export full scrollback history to a file."""
    manager = TermiteManager()
    try:
        manager.export_history(session_name=session, path=path)
    except SessionNotFoundError as e:
        raise click.ClickException(str(e))
    click.echo(f"Exported to {path}")
