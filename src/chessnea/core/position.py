from dataclasses import dataclass

from chessnea.core import types


@dataclass(frozen = True)
class Position:
    board: tuple[tuple[tuple[types.Piece, types.PieceColour], ...], ...]
    sideToMove: types.PieceColour
    castlingRights: frozenset[types.CastlingRights]  # Corresponds to types.CastlingRights LUT
    enPassantTargettableSquare: tuple[int, int]
    fiftyMoveCounter: int
    fullMoveCounter: int