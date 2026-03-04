import time
from pathlib import Path

import libtmux

SOCKET_NAME = "termite"
DEFAULT_WIDTH = 200
DEFAULT_HEIGHT = 50


class SessionNotFoundError(Exception):
    pass


class SessionExistsError(Exception):
    pass


class TermiteManager:
    def __init__(self) -> None:
        self.server = libtmux.Server(socket_name=SOCKET_NAME)

    def list_sessions(self) -> list[str]:
        return [s.session_name for s in self.server.sessions if s.session_name]

    def new_session(self, name: str) -> None:
        if self.server.has_session(name):
            raise SessionExistsError(f"Session '{name}' already exists")
        self.server.new_session(
            session_name=name,
            attach=False,
            x=DEFAULT_WIDTH,
            y=DEFAULT_HEIGHT,
        )

    def kill_session(self, name: str) -> None:
        session = self.server.sessions.get(session_name=name)
        if session is None:
            raise SessionNotFoundError(f"Session '{name}' not found")
        session.kill()

    def read_pane(self, session_name: str, tail_chars: int | None) -> str:
        return self._capture(
            pane=self._get_pane(session_name), full=False, tail_chars=tail_chars
        )

    def send_file(self, session_name: str, file_path: str) -> None:
        pane = self._get_pane(session_name)
        text = Path(file_path).read_text()
        pane.cmd("send-keys", "-l", "--", text)

    def run_command(
        self,
        session_name: str,
        keys: tuple[str, ...],
        yield_time_ms: int | None,
        tail_chars: int | None,
    ) -> str | None:
        pane = self._get_pane(session_name)
        pane.cmd("send-keys", *keys)
        if yield_time_ms is None:
            return None
        time.sleep(yield_time_ms / 1000)
        return self._capture(pane=pane, full=False, tail_chars=tail_chars)

    def export_history(self, session_name: str, path: str) -> None:
        pane = self._get_pane(session_name)
        output = self._capture(pane=pane, full=True, tail_chars=None)
        Path(path).write_text(output + "\n")

    def _get_pane(self, session_name: str) -> libtmux.Pane:
        session = self.server.sessions.get(session_name=session_name)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_name}' not found")
        pane = session.active_window.active_pane
        assert pane is not None
        return pane

    def _capture(self, pane: libtmux.Pane, full: bool, tail_chars: int | None) -> str:
        if full:
            lines = pane.capture_pane(start="-", end="-", join_wrapped=True)
        else:
            lines = pane.capture_pane(join_wrapped=True)
        output = "\n".join(lines)
        if tail_chars is not None:
            output = output[-tail_chars:]
        return output
