from typing import Protocol

import chessnea.enums as enums

class BoardTypes(Protocol):
    Board: list[list[tuple[enums.Piece, enums.PieceColour]]]
    SideToMove: enums.PieceColour
    CastlingRights: list[enums.CastlingRights]
    EnPassantTargettableSquare: tuple[int, int]
    FiftyMoveCounter: int
    FullMoveCounter: int
    piecePickedUp: tuple[int, int]

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

def processMove(board: BoardTypes, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> None:
    fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
    if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
        return # If an empty move; we exit
    moves: list[tuple[int, int, enums.MoveType]] = getPseudoLegalMovesForPiece(board, row = fromRow, col = fromCol)
    # Check whether the move to be processed is a pseudo-legal move
    if (toRow, toCol, enums.MoveType.NORMAL) in moves or (toRow, toCol, enums.MoveType.CAPTURE) in moves or (toRow, toCol, enums.MoveType.EN_PASSANT) in moves or (toRow, toCol, enums.MoveType.CASTLING) in moves or (toRow, toCol, enums.MoveType.PROMOTION) in moves:
        moveType: enums.MoveType = enums.MoveType.NORMAL
        for move in moves: # Assign move type to move to be processed
            if move[0] == toRow and move[1] == toCol:
                moveType = move[2]
                break
        print(f"Board: Processing move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")
        # Process the standard move
        board.Board[toRow][toCol] = board.Board[fromRow][fromCol]
        board.Board[fromRow][fromCol] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)

    # Begin other move type processing
    if (toRow, toCol, enums.MoveType.EN_PASSANT) in moves: # Handle en passant
        if board.Board[fromRow][fromCol][1] == enums.PieceColour.WHITE:
            board.Board[toRow + 1][toCol] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)
        else:
            board.Board[toRow - 1][toCol] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)
    if board.Board[fromRow][fromCol][0] == enums.Piece.PAWN: # Handle pawn logic (setting en passant squares)
        if (fromRow, fromCol) == (toRow + 2, toCol):
            board.EnPassantTargettableSquare = (toRow + 1, toCol)
        elif (fromRow, fromCol) == (toRow - 2, toCol):
            board.EnPassantTargettableSquare = (toRow - 1, toCol)
        else:
            board.EnPassantTargettableSquare = (-1, -1)

    if board.SideToMove == enums.PieceColour.WHITE: # Handle switching side to move flag after each move is processed
        board.SideToMove = enums.PieceColour.BLACK 
    else:
        board.SideToMove = enums.PieceColour.WHITE