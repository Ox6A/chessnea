from dataclasses import dataclass

from chessnea.core import types


@dataclass(frozen = True)
class Position:
    Board: tuple[tuple[tuple[types.Piece, types.PieceColour], ...], ...]
    SideToMove: types.PieceColour
    CastlingRights: frozenset[types.CastlingRights]  # Corresponds to types.CastlingRights LUT
    EnPassantTargettableSquare: tuple[int, int]
    FiftyMoveCounter: int
    FullMoveCounter: int