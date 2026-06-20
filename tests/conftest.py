# pyright: reportAny = false
import os
from pathlib import Path
import sys

_ = os.environ.setdefault(key = "SDL_VIDEODRIVER", value = "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import chessnea.board as boardHandling
import pytest

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
                if name == f"perft_nodes":
                    nodes += int(value)

    terminalreporter.write_line(line = f"Total nodes processed: {nodes}")