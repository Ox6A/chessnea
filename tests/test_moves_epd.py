from pathlib import Path
from dataclasses import dataclass
import os
import pytest
from collections.abc import Callable

import chessnea.board as boardHandling
import chessnea.config as config
import chessnea.fen as fen

MAX_DEPTH = 3
EPD_DIR_PATH: Path = Path(__file__).parent / "epd"
epdList: list[str] = []

for file in os.listdir(path = EPD_DIR_PATH):
    if file.endswith(".epd"):
        epdList.append(file)

@dataclass(frozen = True)
class PerftData:
    line: str
    fen: str
    perft: dict[int, int]

def parseEPDLine(line: str, lineNr: int) -> PerftData | None:
    line = line.strip()
    if line == "" or line.startswith("#"):
        return None
    lineSections: list[str] = line.split(sep = ";")
    fen: str = lineSections[0].strip()
    depths: list[str] = lineSections[1:]

    perft: dict[int, int] = {}

    for content in depths:
        content: str = content.strip()
        if content == "":
            continue
        depthParts: list[str] = content.split(maxsplit = 1)
        if len(depthParts) != 2:
            continue
        prefix, suffix = depthParts
        prefix, suffix = prefix.strip(), suffix.strip()

        if prefix[0] == "D" and prefix[1:].isdigit():
            depth: int = int(prefix[1:])
            nodes: int = int(suffix.split()[0])
            perft[depth] = nodes
    
    if perft == {}:
        return None
    
    return PerftData(
        line = str(lineNr),
        fen = fen,
        perft = perft
    )

def parseEPDFile(path: Path) -> list[PerftData]:
    perftData: list[PerftData] = []

    for lineNr, line in enumerate[str](path.read_text().splitlines(), start = 1):
        data: PerftData | None = parseEPDLine(line = line, lineNr = lineNr)
        if data is not None:
            perftData.append(data)
    
    return perftData

def getBoardHandlingFromFEN(fenString: str) -> boardHandling.BoardHandling:
    board: boardHandling.BoardHandling = boardHandling.BoardHandling()
    fen.importFEN(board = board, fen = fenString)
    board.refreshGameStateAfterFENLoad()
    return board

def runPerft(board: boardHandling.BoardHandling, depth: int) -> int:
    moves: list[config.MoveData] = boardHandling.getAllLegalMovesForSide(board = board, colour = board.SideToMove)
    if depth == 1:
        return len(moves)
    
    n: int = 0
    for move in moves:
        childBoard: boardHandling.BoardHandling = getBoardHandlingFromFEN(fenString = fen.exportFEN(board = board))
        executedMove: bool = boardHandling.processMove(board = childBoard, fromSquare = move.fromSquare, toSquare = move.toSquare)
        if not executedMove:
            raise AssertionError(f"Tried to make move, but failed! {move}")
        if move.moveType == config.MoveType.PROMOTION:
            boardHandling.completePromotion(board = childBoard, promotionPieceType = move.promotionPiece)
        n += runPerft(board = childBoard, depth = depth - 1)
    
    return n

def loadPerft()-> list[tuple[str, str, int, int]]:
    if not EPD_DIR_PATH.exists():
        return []
    if len(epdList) == 0:
        return []

    perftList: list[tuple[str, str, int, int]] = []

    for epd in epdList:
        epdPath: Path = EPD_DIR_PATH / epd
        perftData: list[PerftData] = parseEPDFile(path = epdPath)
        for data in perftData:
            for depth, nodes in data.perft.items():
                if depth <= MAX_DEPTH:
                    perftList.append((data.line, data.fen, depth, nodes))

    return perftList

perftList: list[tuple[str, str, int, int]] = loadPerft()
if perftList == []:
    pytest.skip(reason = "No EPD files found!", allow_module_level = True)

@pytest.mark.parametrize(argnames = ("line", "fenString", "depth", "nodes"), argvalues = perftList)
def testEPDPerftCases(line: str, fenString: str, depth: int, nodes: int, record_property: Callable[[str, object], None]) -> None:
    board: boardHandling.BoardHandling = getBoardHandlingFromFEN(fenString = fenString) 
    actualNodes: int = runPerft(board = board, depth = depth)

    record_property("perft_nodes", actualNodes)

    assert actualNodes == nodes, (
        f"Line {line}. depth {depth} expected {nodes}, got {actualNodes}")