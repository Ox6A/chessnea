#!/usr/bin/python
# noqa: EXE001
from chessnea.app import main
from chessnea.app import fen

if __name__ == "__main__":
    fen.importFENToPositionObject(fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    #main()