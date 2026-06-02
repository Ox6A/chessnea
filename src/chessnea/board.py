from typing import Protocol

import pygame

import chessnea.assets as assets
import chessnea.config as config

class BoardTypes(Protocol):
    Board: list[list[tuple[config.Piece, config.PieceColour]]]
    SideToMove: config.PieceColour
    CastlingRights: list[config.CastlingRights]
    EnPassantTargettableSquare: tuple[int, int]
    FiftyMoveCounter: int
    FullMoveCounter: int
    piecePickedUp: tuple[int, int]

class BoardHandling():
    def __init__(self)  -> None:
        self.Board: list[list[tuple[config.Piece, config.PieceColour]]] = [[(config.Piece.EMPTY, config.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board
        self.SideToMove: config.PieceColour = config.PieceColour.WHITE # White is the default side to move (subject to parsed FEN position)
        self.CastlingRights: list[config.CastlingRights] = [config.CastlingRights.WHITE_KINGSIDE, config.CastlingRights.WHITE_QUEENSIDE, config.CastlingRights.BLACK_KINGSIDE, config.CastlingRights.BLACK_QUEENSIDE]
        self.EnPassantTargettableSquare: tuple[int, int] = (-1, -1) # Defines which square is attackable under en passant
        self.FiftyMoveCounter: int = 0 # Niche rule allowing a draw after 50 moves without a capture
        self.FullMoveCounter: int = 0 # Constant tracking for current move nr.
        self.sprites: list[list[pygame.Surface | None]] = assets.loadSprites() # Load sprites from disk
        self.piecePickedUp: tuple[int, int] = (-1, -1) # Current piece picked up by the mouse cursor

    def getSquareUnderMousePosition(self) -> tuple[int, int] | None:
        # Converts absolute coordinates for the mouse position provided by Pygame into a internal board square
        mouseX, mouseY = pygame.mouse.get_pos()
        col: int = mouseX // config.WIDTH_PER_SQUARE
        row: int = mouseY // config.HEIGHT_PER_SQUARE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        else:
            return None

def getPseudoLegalMovesForPiece(board: BoardTypes, row: int, col: int) -> list[tuple[int, int, config.MoveType]]:
    # In order to get all legal moves, we get all pseudo-legal moves (ignoring check conditions)
    validMoves: list[tuple[int, int, config.MoveType]] = []
    if board.Board[row][col][0] == config.Piece.EMPTY: # Standard move
        return [(-1, -1, config.MoveType.NORMAL)]
    elif board.Board[row][col][0] == config.Piece.PAWN: # Handle pawn logic (NEED A REFACTOR)
        if board.Board[row][col][1] == config.PieceColour.WHITE:
            if row - 1 >= 0:
                if board.Board[row - 1][col][0] == config.Piece.EMPTY:
                    if row == 6:
                        if board.Board[row - 2][col][0] == config.Piece.EMPTY:
                            validMoves.append((row - 1, col, config.MoveType.NORMAL))
                            validMoves.append((row - 2, col, config.MoveType.NORMAL))
                    else:
                        validMoves.append((row - 1, col, config.MoveType.NORMAL))
            if row - 1 >= 0 and col + 1 <= 7:
                if (board.Board[row - 1][col + 1][0] != config.Piece.EMPTY and 
                    board.Board[row - 1][col + 1][0] != config.Piece.KING and 
                    board.Board[row - 1][col + 1][1] != board.Board[row][col][1]):
                    validMoves.append((row - 1, col + 1, config.MoveType.CAPTURE))
                if (row - 1, col + 1) == board.EnPassantTargettableSquare and board.Board[row - 1][col + 1][0] == config.Piece.EMPTY:
                    validMoves.append((row - 1, col + 1, config.MoveType.EN_PASSANT))
                #if (((row - 1, col + 1) == self.EnPassantTargettableSquare and
                    #(self.Board[row - 1][col + 1][1] != self.Board[row][col][1])) or
                    #(self.Board[row - 1][col + 1][0] == config.Piece.EMPTY)):
                    #validMoves.append((row - 1, col + 1, config.MoveType.EN_PASSANT))
            if row - 1 >= 0 and col - 1 >= 0:
                if (board.Board[row - 1][col - 1][0] != config.Piece.EMPTY and 
                    board.Board[row - 1][col - 1][0] != config.Piece.KING and  
                    board.Board[row - 1][col - 1][1] != board.Board[row][col][1]):
                    validMoves.append((row - 1, col - 1, config.MoveType.CAPTURE))
                if (row - 1, col - 1) == board.EnPassantTargettableSquare:
                    validMoves.append((row - 1, col - 1, config.MoveType.EN_PASSANT))
        else:
            if row + 1 <= 7:
                if board.Board[row + 1][col][0] == config.Piece.EMPTY:
                    if row == 1:
                        if board.Board[row + 2][col][0] == config.Piece.EMPTY:
                            validMoves.append((row + 1, col, config.MoveType.NORMAL))
                            validMoves.append((row + 2, col, config.MoveType.NORMAL))
                    else:
                        validMoves.append((row + 1, col, config.MoveType.NORMAL))
            if row + 1 <= 7 and col + 1 <= 7:
                if (board.Board[row + 1][col + 1][0] != config.Piece.EMPTY and 
                    board.Board[row + 1][col + 1][0] != config.Piece.KING and 
                    board.Board[row + 1][col + 1][1] != board.Board[row][col][1]):
                    validMoves.append((row + 1, col + 1, config.MoveType.CAPTURE))
                if (row + 1, col + 1) == board.EnPassantTargettableSquare:
                    validMoves.append((row + 1, col + 1, config.MoveType.EN_PASSANT))
            if row + 1 <= 7 and col - 1 >= 0:
                if (board.Board[row + 1][col - 1][0] != config.Piece.EMPTY and 
                    board.Board[row + 1][col - 1][0] != config.Piece.KING and
                    board.Board[row + 1][col - 1][1] != board.Board[row][col][1]):
                    validMoves.append((row + 1, col - 1, config.MoveType.CAPTURE))
                if (row + 1, col - 1) == board.EnPassantTargettableSquare:
                    validMoves.append((row + 1, col - 1, config.MoveType.EN_PASSANT))
        return validMoves
    return [(-1, -1, config.MoveType.NORMAL)]

def processMove(board: BoardTypes, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> None:
    fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
    if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
        return # If an empty move; we exit
    moves: list[tuple[int, int, config.MoveType]] = getPseudoLegalMovesForPiece(board, row = fromRow, col = fromCol)
    # Check whether the move to be processed is a pseudo-legal move
    if (toRow, toCol, config.MoveType.NORMAL) in moves or (toRow, toCol, config.MoveType.CAPTURE) in moves or (toRow, toCol, config.MoveType.EN_PASSANT) in moves or (toRow, toCol, config.MoveType.CASTLING) in moves or (toRow, toCol, config.MoveType.PROMOTION) in moves:
        moveType: config.MoveType = config.MoveType.NORMAL
        for move in moves: # Assign move type to move to be processed
            if move[0] == toRow and move[1] == toCol:
                moveType = move[2]
                break
        print(f"Board: Processing move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")
        # Process the standard move
        board.Board[toRow][toCol] = board.Board[fromRow][fromCol]
        board.Board[fromRow][fromCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)

    # Begin other move type processing
    if (toRow, toCol, config.MoveType.EN_PASSANT) in moves: # Handle en passant
        if board.Board[fromRow][fromCol][1] == config.PieceColour.WHITE:
            board.Board[toRow + 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
        else:
            board.Board[toRow - 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
    if board.Board[fromRow][fromCol][0] == config.Piece.PAWN: # Handle pawn logic (setting en passant squares)
        if (fromRow, fromCol) == (toRow + 2, toCol):
            board.EnPassantTargettableSquare = (toRow + 1, toCol)
        elif (fromRow, fromCol) == (toRow - 2, toCol):
            board.EnPassantTargettableSquare = (toRow - 1, toCol)
        else:
            board.EnPassantTargettableSquare = (-1, -1)

    if board.SideToMove == config.PieceColour.WHITE: # Handle switching side to move flag after each move is processed
        board.SideToMove = config.PieceColour.BLACK 
    else:
        board.SideToMove = config.PieceColour.WHITE