# pyright: reportAny = false
import os
import pytest

import chessnea.board as boardHandling

_ = os.environ.setdefault(key="SDL_VIDEODRIVER", value="dummy")

@pytest.fixture
def newBoard() -> boardHandling.BoardHandling:
    board = boardHandling.BoardHandling()
    _ = board.resetBoard()
    return board

def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter) -> None:
    nodes: int = 0
    for reports in terminalreporter.stats.values():
        for report in reports:
            if getattr(report, "when", None) != "call":
                continue
            for name, value in getattr(report, "user_properties", []):
                if name == "perft_nodes":
                    nodes += int(value)

    terminalreporter.write_line(line = f"Total nodes processed: {nodes}")