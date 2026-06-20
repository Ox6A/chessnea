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
