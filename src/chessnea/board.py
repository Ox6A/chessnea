import logging
import pygame

import chessnea.assets as assets
import chessnea.config as config

logger: logging.Logger = logging.getLogger(__name__)

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

class PseudoLegalMovesForPieceType():
    @staticmethod
    def pawn(board: BoardHandling, row: int, col: int) -> list[tuple[int, int, config.MoveType]]:
        validMoves: list[tuple[int, int, config.MoveType]] = []
        direction: int
        startingRank: int

        if board.Board[row][col][1] == config.PieceColour.WHITE:
            direction = -1
            startingRank = 6
        else:
            direction = 1
            startingRank = 1
        
        targetSingleRow: int = row + direction
        targetDoubleRow: int = row + (2 * direction)
        if 0 <= targetSingleRow <= 7 and board.Board[targetSingleRow][col][0] == config.Piece.EMPTY: # Standard move
            validMoves.append((targetSingleRow, col, config.MoveType.NORMAL))
            if row == startingRank and board.Board[targetDoubleRow][col][0] == config.Piece.EMPTY: # Double move from starting rank
                validMoves.append((targetDoubleRow, col, config.MoveType.NORMAL))

        for targetDiagonalCol in [col -1, col + 1]: # Captures
            if 0 <= targetDiagonalCol <= 7 and 0 <= targetSingleRow <= 7:
                targetPiece, targetColour = board.Board[targetSingleRow][targetDiagonalCol][0], board.Board[targetSingleRow][targetDiagonalCol][1]
                if targetPiece != config.Piece.EMPTY and targetPiece != config.Piece.KING and targetColour != board.Board[row][col][1]: # Diagonal capture
                    validMoves.append((targetSingleRow, targetDiagonalCol, config.MoveType.CAPTURE))
                if (targetSingleRow, targetDiagonalCol) == board.EnPassantTargettableSquare and targetPiece == config.Piece.EMPTY: # En passant capture
                    validMoves.append((targetSingleRow, targetDiagonalCol, config.MoveType.EN_PASSANT))
        return validMoves

    @staticmethod
    def bishop(board: BoardHandling, row: int, col: int) -> list[tuple[int, int, config.MoveType]]:
        validMoves: list[tuple[int, int, config.MoveType]] = []
        currentColour = board.Board[row][col][1]
        directions: list[list[int]] = [[-1, -1], [-1, 1], [1, -1], [1, 1]] # Up Left, Up Right, Down Left, Down Right
        targetRow: int
        targetCol: int

        for i in directions:
            targetRow, targetCol = row + i[0], col + i[1]
            while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
                targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
                if targetPiece == config.Piece.EMPTY:
                    validMoves.append((targetRow, targetCol, config.MoveType.NORMAL))
                elif targetColour == currentColour:
                    break
                elif targetPiece != config.Piece.KING:
                    validMoves.append((targetRow, targetCol, config.MoveType.CAPTURE))
                    break
                targetRow, targetCol = targetRow + i[0], targetCol + i[1]
        return validMoves

def getPseudoLegalMovesForPiece(board: BoardHandling, row: int, col: int) -> list[tuple[int, int, config.MoveType]]:
    # In order to get all legal moves, we get all pseudo-legal moves (ignoring check conditions)
    if board.Board[row][col][0] == config.Piece.EMPTY:
        return []
    elif board.Board[row][col][0] == config.Piece.PAWN:
        return PseudoLegalMovesForPieceType.pawn(board, row, col)
    elif board.Board[row][col][0] == config.Piece.BISHOP:
        return PseudoLegalMovesForPieceType.bishop(board, row, col)
    return []

def processMove(board: BoardHandling, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> None:
    fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
    if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
        return # If an empty move; we exit
    moves: list[tuple[int, int, config.MoveType]] = getPseudoLegalMovesForPiece(board, row = fromRow, col = fromCol)
    pieceToMove, colourToMove = board.Board[fromRow][fromCol][0], board.Board[fromRow][fromCol][1]

    # Check whether the move to be processed is a pseudo-legal move
    moveType: config.MoveType | None = None
    for move in moves:
        moveRow, moveCol, moveMoveType = move
        if moveRow == toRow and moveCol == toCol:
            moveType = moveMoveType
            break
    if moveType is None:
        logger.info(msg = f"Board: Invalid move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}")
        return
    logger.info(msg = f"Board: Processing move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")

    board.Board[toRow][toCol] = board.Board[fromRow][fromCol]
    board.Board[fromRow][fromCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)

    # Begin other move type processing
    if moveType == config.MoveType.EN_PASSANT: # Handle en passant
        if colourToMove == config.PieceColour.WHITE:
            board.Board[toRow + 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
        else:
            board.Board[toRow - 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
    if pieceToMove == config.Piece.PAWN: # Handle pawn logic (setting en passant squares)
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
