import chessnea.fen as fen
import chessnea.board as boardHandling
import chessnea.config as config

def testFENExportWithStartingPosition(newBoard: boardHandling.BoardHandling) -> None:
    assert fen.exportFEN(board = newBoard) == config.FEN_STARTING_POSITION