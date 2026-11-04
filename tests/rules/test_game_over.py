"""Tests game over detection"""

import pytest

from chessnea.core import fen, types
from chessnea.rules import legal, moves

GAME_OVER_CASES: list[tuple[str, str, types.GameOverReason | None]] = [
	("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", None),
	("Fool's mate", "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3", types.GameOverReason.CHECKMATE),
	("Back rank mate", "R5k1/5ppp/8/8/8/8/8/6K1 b - - 1 1", types.GameOverReason.CHECKMATE),
	("King and queen stalemate", "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1", types.GameOverReason.STALEMATE),
	("King vs king", "8/8/4k3/8/8/4K3/8/8 w - - 0 1", types.GameOverReason.INSUFFICIENT_MATERIAL),
	("King and bishop vs king", "8/8/4k3/8/8/4KB2/8/8 w - - 0 1", types.GameOverReason.INSUFFICIENT_MATERIAL),
	("King and knight vs king", "8/8/4k3/8/8/4KN2/8/8 w - - 0 1", types.GameOverReason.INSUFFICIENT_MATERIAL),
	("Bishops on the same colour squares", "8/8/2b1k3/8/8/4KB2/8/8 w - - 0 1", types.GameOverReason.INSUFFICIENT_MATERIAL),
	("Bishops on opposite colour squares", "8/8/3bk3/8/8/4KB2/8/8 w - - 0 1", None),
	("King and two bishops vs king", "8/8/4k3/8/8/4KBB1/8/8 w - - 0 1", None),
	("Knight each", "8/8/3nk3/8/8/4KN2/8/8 w - - 0 1", None),
	("King and pawn vs king", "8/8/4k3/8/8/4KP2/8/8 w - - 0 1", None),
	("King and rook vs king", "8/8/4k3/8/8/4KR2/8/8 w - - 0 1", None),
	("Fifty-move rule reached", "4k3/8/8/8/8/8/8/R3K3 w - - 100 60", types.GameOverReason.FIFTY_MOVE_RULE),
	("One half-move before the fifty-move rule", "4k3/8/8/8/8/8/8/R3K3 w - - 99 60", None),
]

@pytest.mark.parametrize(argnames = "description, fenString, expectedReason", argvalues = GAME_OVER_CASES)
def testGameOverStateFromFEN(description: str, fenString: str, expectedReason: types.GameOverReason | None) -> None:
	position: types.Position = fen.importFENToPositionObject(fen = fenString)
	positionHistory: list[types.PositionIdentifier] = [legal.returnPositionIdentifierFromPosition(position = position)]
	actualReason: types.GameOverReason | None = legal.getGameOverState(position = position, positionHistory = positionHistory)
	assert actualReason == expectedReason, description

def testCheckmateBeatsFiftyMoveRule() -> None:
	position: types.Position = fen.importFENToPositionObject(fen = "6k1/5ppp/8/8/8/8/8/R5K1 w - - 99 1")
	backRankMate: types.Move = types.Move(fromSquare = (7, 0), toSquare = (0, 0))
	position = moves.applyMove(position = position, move = backRankMate)
	positionHistory: list[types.PositionIdentifier] = [legal.returnPositionIdentifierFromPosition(position = position)]
	assert position.fiftyMoveCounter == 100
	assert legal.getGameOverState(position = position, positionHistory = positionHistory) == types.GameOverReason.CHECKMATE

def testThreefoldRepetitionByKnightShuffle() -> None:
	position: types.Position = fen.importFENToPositionObject(fen = "4k1n1/8/8/8/8/8/8/4K1N1 w - - 0 1")
	positionHistory: list[types.PositionIdentifier] = [legal.returnPositionIdentifierFromPosition(position = position)]
	knightShuffle: list[types.Move] = [
		types.Move(fromSquare = (7, 6), toSquare = (5, 5)), # Ng1-f3
		types.Move(fromSquare = (0, 6), toSquare = (2, 5)), # Ng8-f6
		types.Move(fromSquare = (5, 5), toSquare = (7, 6)), # Nf3-g1
		types.Move(fromSquare = (2, 5), toSquare = (0, 6)), # Nf6-g8
	] * 2

	for halfMoveNumber, move in enumerate(knightShuffle, start = 1):
		position = moves.applyMove(position = position, move = move)
		positionHistory.append(legal.returnPositionIdentifierFromPosition(position = position))
		actualReason: types.GameOverReason | None = legal.getGameOverState(position = position, positionHistory = positionHistory)
		if halfMoveNumber < len(knightShuffle):
			assert actualReason is None, f"Game ended early on half-move {halfMoveNumber}"
		else:
			assert actualReason == types.GameOverReason.THREEFOLD_REPETITION
