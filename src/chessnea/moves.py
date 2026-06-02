from typing import Protocol

import chessnea.enums as enums

class BoardTypes(Protocol):
    Board: list[list[tuple[enums.Piece, enums.PieceColour]]]
    SideToMove: enums.PieceColour
    CastlingRights: list[enums.CastlingRights]
    EnPassantTargettableSquare: tuple[int, int]
    FiftyMoveCounter: int
    FullMoveCounter: int

def getPseudoLegalMovesForPiece(board: BoardTypes, row: int, col: int) -> list[tuple[int, int, enums.MoveType]]:
    # In order to get all legal moves, we get all pseudo-legal moves (ignoring check conditions)
    validMoves: list[tuple[int, int, enums.MoveType]] = []
    if board.Board[row][col][0] == enums.Piece.EMPTY: # Standard move
        return [(-1, -1, enums.MoveType.NORMAL)]
    elif board.Board[row][col][0] == enums.Piece.PAWN: # Handle pawn logic (NEED A REFACTOR)
        if board.Board[row][col][1] == enums.PieceColour.WHITE:
            if row - 1 >= 0:
                if board.Board[row - 1][col][0] == enums.Piece.EMPTY:
                    if row == 6:
                        if board.Board[row - 2][col][0] == enums.Piece.EMPTY:
                            validMoves.append((row - 1, col, enums.MoveType.NORMAL))
                            validMoves.append((row - 2, col, enums.MoveType.NORMAL))
                    else:
                        validMoves.append((row - 1, col, enums.MoveType.NORMAL))
            if row - 1 >= 0 and col + 1 <= 7:
                if (board.Board[row - 1][col + 1][0] != enums.Piece.EMPTY and 
                    board.Board[row - 1][col + 1][0] != enums.Piece.KING and 
                    board.Board[row - 1][col + 1][1] != board.Board[row][col][1]):
                    validMoves.append((row - 1, col + 1, enums.MoveType.CAPTURE))
                if (row - 1, col + 1) == board.EnPassantTargettableSquare and board.Board[row - 1][col + 1][0] == enums.Piece.EMPTY:
                    validMoves.append((row - 1, col + 1, enums.MoveType.EN_PASSANT))
                #if (((row - 1, col + 1) == self.EnPassantTargettableSquare and
                    #(self.Board[row - 1][col + 1][1] != self.Board[row][col][1])) or
                    #(self.Board[row - 1][col + 1][0] == enums.Piece.EMPTY)):
                    #validMoves.append((row - 1, col + 1, enums.MoveType.EN_PASSANT))
            if row - 1 >= 0 and col - 1 >= 0:
                if (board.Board[row - 1][col - 1][0] != enums.Piece.EMPTY and 
                    board.Board[row - 1][col - 1][0] != enums.Piece.KING and  
                    board.Board[row - 1][col - 1][1] != board.Board[row][col][1]):
                    validMoves.append((row - 1, col - 1, enums.MoveType.CAPTURE))
                if (row - 1, col - 1) == board.EnPassantTargettableSquare:
                    validMoves.append((row - 1, col - 1, enums.MoveType.EN_PASSANT))
        else:
            if row + 1 <= 7:
                if board.Board[row + 1][col][0] == enums.Piece.EMPTY:
                    if row == 1:
                        if board.Board[row + 2][col][0] == enums.Piece.EMPTY:
                            validMoves.append((row + 1, col, enums.MoveType.NORMAL))
                            validMoves.append((row + 2, col, enums.MoveType.NORMAL))
                    else:
                        validMoves.append((row + 1, col, enums.MoveType.NORMAL))
            if row + 1 <= 7 and col + 1 <= 7:
                if (board.Board[row + 1][col + 1][0] != enums.Piece.EMPTY and 
                    board.Board[row + 1][col + 1][0] != enums.Piece.KING and 
                    board.Board[row + 1][col + 1][1] != board.Board[row][col][1]):
                    validMoves.append((row + 1, col + 1, enums.MoveType.CAPTURE))
                if (row + 1, col + 1) == board.EnPassantTargettableSquare:
                    validMoves.append((row + 1, col + 1, enums.MoveType.EN_PASSANT))
            if row + 1 <= 7 and col - 1 >= 0:
                if (board.Board[row + 1][col - 1][0] != enums.Piece.EMPTY and 
                    board.Board[row + 1][col - 1][0] != enums.Piece.KING and 
                    board.Board[row + 1][col - 1][1] != board.Board[row][col][1]):
                    validMoves.append((row + 1, col - 1, enums.MoveType.CAPTURE))
                if (row + 1, col - 1) == board.EnPassantTargettableSquare:
                    validMoves.append((row + 1, col - 1, enums.MoveType.EN_PASSANT))
        return validMoves
    return [(-1, -1, enums.MoveType.NORMAL)]