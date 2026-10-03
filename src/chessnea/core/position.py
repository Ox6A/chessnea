from dataclasses import dataclass

from chessnea.core import types


@dataclass(frozen = True)
class Position:
    board: types.Board
    sideToMove: types.PieceColour
    castlingRights: frozenset[types.CastlingRights]  # Corresponds to types.CastlingRights LUT
    enPassantTargettableSquare: types.Square | None
    fiftyMoveCounter: int
    fullMoveCounter: int