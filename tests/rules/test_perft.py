"""Tests legal move generation by counting every reachable position (perft) and comparing against known totals."""

import pytest

from chessnea.core import fen, types
from chessnea.rules import legal, moves
from tests.helper import loadEPD

# Deepest depth to test
MAX_PERFT_DEPTH: int = 3

def countPerftPositions(position: types.Position, depth: int) -> int:
	"""Counts the positions reachable from the given position in 'depth' legal half-moves.

	Args:
		position: The position to start searching from.
		depth: Number of halfmoves left to play.

	Returns:
		The number of positions reached once depth reaches 0.
	"""
	if depth == 0:
		return 1

	reachedPositionCount: int = 0
	for legalMove in legal.getAllLegalMoves(position = position):
		positionAfterMove: types.Position = moves.applyMove(position = position, move = legalMove)
		reachedPositionCount += countPerftPositions(position = positionAfterMove, depth = depth - 1)
	return reachedPositionCount

def loadEPDPerftCases() -> list[tuple[str, int, int]]:
	"""Reads the EPD file and splits each line into individual (FEN, depth, expected count) tuples for testing.

	Returns:
		A list of (FEN string, depth, expected position count) tuples
	"""
	perftCases: list[tuple[str, int, int]] = []
	for epdLine in loadEPD():
		if not epdLine:
			continue

		# First field is the FEN, every field after it is a "D<depth> <count>" entry
		epdFields: list[str] = [field.strip() for field in epdLine.split(";")]
		fenString: str = epdFields[0]
		depthEntries: list[str] = epdFields[1:]

		for depthEntry in depthEntries:
			depthLabel, expectedCountText = depthEntry.split()
			depth: int = int(depthLabel[1:]) # Remove the "D"
			expectedPositionCount: int = int(expectedCountText)
			if depth <= MAX_PERFT_DEPTH:
				perftCases.append((fenString, depth, expectedPositionCount))
	return perftCases

@pytest.mark.parametrize(argnames = "fenString, depth, expectedPositionCount", argvalues = loadEPDPerftCases())
def testPerftFromEPDFile(fenString: str, depth: int, expectedPositionCount: int) -> None:
	"""Checks the perft count for each position and depth listed in the EPD file."""
	startPosition: types.Position = fen.importFENToPositionObject(fen = fenString)
	actualPositionCount: int = countPerftPositions(position = startPosition, depth = depth)
	assert actualPositionCount == expectedPositionCount