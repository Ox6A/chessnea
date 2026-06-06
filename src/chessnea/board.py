from typing import Literal
import logging
import pygame

import chessnea.assets as assets
import chessnea.config as config

logger: logging.Logger = logging.getLogger(__name__)

class BoardHandling():
    def __init__(self)  -> None:
        self.Board: list[list[tuple[config.Piece, config.PieceColour]]] = [
                [
                (config.Piece.EMPTY, config.PieceColour.WHITE) for _ in range(8)
                ] for _ in range(8)
            ] # Initialise an empty board
        self.SideToMove: config.PieceColour = config.PieceColour.WHITE # White is the default side to move (subject to parsed FEN position)
        self.CastlingRights: list[config.CastlingRights] = [config.CastlingRights.WHITE_KINGSIDE, config.CastlingRights.WHITE_QUEENSIDE, config.CastlingRights.BLACK_KINGSIDE, config.CastlingRights.BLACK_QUEENSIDE]
        self.EnPassantTargettableSquare: tuple[int, int] = (-1, -1) # Defines which square is attackable under en passant
        self.FiftyMoveCounter: int = 0 # Niche rule allowing a draw after 50 moves without a capture
        self.FullMoveCounter: int = 0 # Constant tracking for current move nr.
        self.sprites: list[list[pygame.Surface | None]] = [] # Load sprites from disk
        self.piecePickedUp: tuple[int, int] = (-1, -1) # Current piece picked up by the mouse cursor
        self.piecePickedUpLegalMoves: list[config.MoveData] = [] # Legal moves cache for the currently picked up piece
        self.pendingPromotion: config.PromotionData | None = None # Hold the intended promotion move in place as we wait for user input
        
    def loadSpritesForBoard(self) -> None:
        self.sprites = assets.loadSprites()

    def getSquareUnderMousePosition(self) -> tuple[int, int] | None:
        # Converts absolute coordinates for the mouse position provided by Pygame into a internal board square
        mouseX, mouseY = pygame.mouse.get_pos()
        col: int = mouseX // config.WIDTH_PER_SQUARE
        row: int = mouseY // config.HEIGHT_PER_SQUARE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        else:
            return None
    
    def changeSideToMove(self) -> None:
        if self.SideToMove == config.PieceColour.WHITE:
            self.SideToMove = config.PieceColour.BLACK
        else:
            self.SideToMove = config.PieceColour.WHITE

class PseudoLegalMovesForPieceType():
    @staticmethod
    def pawn(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
        validMoves: list[config.MoveData] = []
        direction: int
        startingRank: int
        moveTypeToUse: config.MoveType

        if board.Board[row][col][1] == config.PieceColour.WHITE:
            direction = -1
            startingRank = 6
        else:
            direction = 1
            startingRank = 1
        targetSingleRow: int = row + direction
        targetDoubleRow: int = row + (2 * direction)
        if 0 <= targetSingleRow <= 7 and board.Board[targetSingleRow][col][0] == config.Piece.EMPTY: # Standard move
            moveTypeToUse = config.MoveType.NORMAL
            if targetSingleRow == 0 or targetSingleRow == 7: # A single row push should be a promotion if landing on the final ranks
                moveTypeToUse = config.MoveType.PROMOTION
            validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, col), moveType = moveTypeToUse))
            if row == startingRank and board.Board[targetDoubleRow][col][0] == config.Piece.EMPTY: # Double move from starting rank
                validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetDoubleRow, col), moveType = config.MoveType.NORMAL))

        for targetDiagonalCol in [col -1, col + 1]: # Captures
            if 0 <= targetDiagonalCol <= 7 and 0 <= targetSingleRow <= 7:
                targetPiece, targetColour = board.Board[targetSingleRow][targetDiagonalCol][0], board.Board[targetSingleRow][targetDiagonalCol][1]
                if targetPiece != config.Piece.EMPTY and targetPiece != config.Piece.KING and targetColour != board.Board[row][col][1]: # Diagonal capture
                    moveTypeToUse = config.MoveType.CAPTURE
                    if targetSingleRow == 0 or targetSingleRow == 7: # A capture should be a promotion if landing on the final ranks
                        moveTypeToUse = config.MoveType.PROMOTION
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = moveTypeToUse))
                if (targetSingleRow, targetDiagonalCol) == board.EnPassantTargettableSquare and targetPiece == config.Piece.EMPTY: # En passant capture
                    if board.SideToMove == config.PieceColour.WHITE:
                        if board.Board[targetSingleRow + 1][targetDiagonalCol][0] == config.Piece.PAWN:
                            if board.Board[targetSingleRow + 1][targetDiagonalCol][1] == config.PieceColour.BLACK:
                                validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = config.MoveType.EN_PASSANT))
                    else:
                        if board.Board[targetSingleRow - 1][targetDiagonalCol][0] == config.Piece.PAWN:
                            if board.Board[targetSingleRow - 1][targetDiagonalCol][1] == config.PieceColour.WHITE:
                                validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = config.MoveType.EN_PASSANT))
        if direction == -1 and targetSingleRow == 0: # Promotion
            ...
        elif direction == 1 and targetSingleRow == 7:
            ...

        return validMoves

    @staticmethod
    def bishop(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
        validMoves: list[config.MoveData] = []
        _, currentColour = board.Board[row][col][0], board.Board[row][col][1]
        directions: list[list[int]] = [[-1, -1], [-1, 1], [1, -1], [1, 1]] # Up Left, Up Right, Down Left, Down Right
        targetRow: int
        targetCol: int

        for i in directions:
            targetRow, targetCol = row + i[0], col + i[1]
            while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
                targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
                if targetPiece == config.Piece.EMPTY:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
                elif targetColour == currentColour:
                    break
                else:
                    if targetPiece != config.Piece.KING:
                        validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
                    break
                targetRow, targetCol = targetRow + i[0], targetCol + i[1]
        return validMoves

    @staticmethod
    def knight(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
        validMoves: list[config.MoveData] = []
        _, currentColour = board.Board[row][col][0], board.Board[row][col][1]
        # Up 2 Left 1, Up 2 Right 1, Up 1 Left 2, Up 1 Right 2, Down 1 Left 2, Down 1 Right 2, Down 2 Left 1, Down 2 Right 1
        directions: list[list[int]] = [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]]
        targetRow: int
        targetCol: int

        for i in directions:
            targetRow, targetCol = row + i[0], col + i[1]
            if 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
                targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
                if targetPiece == config.Piece.EMPTY:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
                elif targetPiece != config.Piece.KING and targetColour != currentColour:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
                targetRow, targetCol = targetRow + i[0], targetCol + i[1]
        return validMoves

    @staticmethod
    def rook(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
        validMoves: list[config.MoveData] = []
        _, currentColour = board.Board[row][col][0], board.Board[row][col][1]
        directions: list[list[int]] = [[-1, 0], [1, 0], [0, -1], [0, 1]] # Up, Down, Left, Right
        targetRow: int
        targetCol: int

        for i in directions:
            targetRow, targetCol = row + i[0], col + i[1]
            while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
                targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
                if targetPiece == config.Piece.EMPTY:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
                elif targetColour == currentColour:
                    break
                else:
                    if targetPiece != config.Piece.KING:
                        validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
                    break
                targetRow, targetCol = targetRow + i[0], targetCol + i[1]
        return validMoves

    @staticmethod
    def queen(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
        validMoves: list[config.MoveData] = []
        _, currentColour = board.Board[row][col][0], board.Board[row][col][1]
        # Up Left, Up, Up Right, Left, Right, Down Left, Down, Down Right
        directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
        targetRow: int
        targetCol: int

        for i in directions:
            targetRow, targetCol = row + i[0], col + i[1]
            while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
                targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
                if targetPiece == config.Piece.EMPTY:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
                elif targetColour == currentColour:
                    break
                else:
                    if targetPiece != config.Piece.KING:
                        validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
                    break
                targetRow, targetCol = targetRow + i[0], targetCol + i[1]
        return validMoves

    @staticmethod
    def king(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
        validMoves: list[config.MoveData] = []
        _, currentColour = board.Board[row][col][0], board.Board[row][col][1]
        directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] # All 8 possible king move directions
        targetRow: int
        targetCol: int

        for i in directions:
            targetRow, targetCol = row + i[0], col + i[1]
            if 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
                targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
                if targetPiece == config.Piece.EMPTY:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
                elif targetPiece != config.Piece.KING and targetColour != currentColour:
                    validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
                targetRow, targetCol = targetRow + i[0], targetCol + i[1]
        return validMoves

def getPseudoLegalMovesForPiece(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
    # In order to get all legal moves, we get all pseudo-legal moves (ignoring check conditions)
    moves: list[config.MoveData] = []
    if board.Board[row][col][0] == config.Piece.EMPTY:
        return []
    elif board.Board[row][col][0] == config.Piece.PAWN:
        logger.debug(msg = f"Board: Getting pseudo-legal moves for pawn at square {(row, col)}")
        moves =  PseudoLegalMovesForPieceType.pawn(board, row, col)
    elif board.Board[row][col][0] == config.Piece.BISHOP:
        logger.debug(msg = f"Board: Getting pseudo-legal moves for bishop at square {(row, col)}")
        moves = PseudoLegalMovesForPieceType.bishop(board, row, col)
    elif board.Board[row][col][0] == config.Piece.KNIGHT:
        logger.debug(msg = f"Board: Getting pseudo-legal moves for knight at square {(row, col)}")
        moves = PseudoLegalMovesForPieceType.knight(board, row, col)
    elif board.Board[row][col][0] == config.Piece.ROOK:
        logger.debug(msg = f"Board: Getting pseudo-legal moves for rook at square {(row, col)}")
        moves = PseudoLegalMovesForPieceType.rook(board, row, col)
    elif board.Board[row][col][0] == config.Piece.QUEEN:
        logger.debug(msg = f"Board: Getting pseudo-legal moves for queen at square {(row, col)}")
        moves = PseudoLegalMovesForPieceType.queen(board, row, col)
    elif board.Board[row][col][0] == config.Piece.KING:
        logger.debug(msg = f"Board: Getting pseudo-legal moves for king at square {(row, col)}")
        moves = PseudoLegalMovesForPieceType.king(board, row, col)
    else:
        logger.error(msg = f"Board: Invalid piece type {board.Board[row][col][0]} at square {(row, col)}")
    return moves

def findKing(board: BoardHandling, sourceColour: config.PieceColour) -> tuple[int, int] | tuple[Literal[-1], Literal[-1]]:
    kingPosition: tuple[int, int] = (-1, -1)
    for rankIndex, rank in enumerate[list[tuple[config.Piece, config.PieceColour]]](board.Board):
        for fileIndex, file in enumerate[tuple[config.Piece, config.PieceColour]](rank):
            if file[0] == config.Piece.KING and file[1] == sourceColour:
                kingPosition = (rankIndex, fileIndex)
                return kingPosition
    return kingPosition

class squareAttackChecking():
    @staticmethod
    def pawn(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
        targetRow, targetCol = targetSquare
        direction: int
        if attackingColour == config.PieceColour.WHITE:
            direction = 1
        else:
            direction = -1
        for potentialPieceDiagonalCol in [targetCol - 1, targetCol + 1]:
            if 0 <= potentialPieceDiagonalCol <= 7 and 0 <= targetRow + direction <= 7:
                if board.Board[targetRow + direction][potentialPieceDiagonalCol][0] == config.Piece.PAWN and board.Board[targetRow + direction][potentialPieceDiagonalCol][1] == attackingColour:
                    return True
        return False

    @staticmethod
    def bishop(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
        targetRow, targetCol = targetSquare
        directions: list[list[int]] = [[-1, -1], [-1, 1], [1, -1], [1, 1]] # Up Left, Up Right, Down Left, Down Right
        for i in directions:
            targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
            while 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
                if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.BISHOP and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
                    return True
                if board.Board[targetRowDirection][targetColDirection][0] != config.Piece.EMPTY:
                    break
                targetRowDirection, targetColDirection = targetRowDirection + i[0], targetColDirection + i[1]
        return False

    @staticmethod
    def knight(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
        targetRow, targetCol = targetSquare
        directions: list[list[int]] = [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]] # Up 2 Left 1, Up 2 Right 1, Up 1 Left 2, Up 1 Right 2, Down 1 Left 2, Down 1 Right 2, Down 2 Left 1, Down 2 Right 1
        for i in directions:
            targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
            if 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
                if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.KNIGHT and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
                    return True
        return False

    @staticmethod
    def rook(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
        targetRow, targetCol = targetSquare
        directions: list[list[int]] = [[-1, 0], [1, 0], [0, -1], [0, 1]] # Up, Down, Left, Right
        for i in directions:
            targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
            while 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
                if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.ROOK and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
                    return True
                if board.Board[targetRowDirection][targetColDirection][0] != config.Piece.EMPTY:
                    break
                targetRowDirection, targetColDirection = targetRowDirection + i[0], targetColDirection + i[1]
        return False

    @staticmethod
    def queen(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
        targetRow, targetCol = targetSquare
        directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] # Up Left, Up, Up Right, Left, Right, Down Left, Down, Down Right
        for i in directions:
            targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
            while 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
                if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.QUEEN and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
                    return True 
                if board.Board[targetRowDirection][targetColDirection][0] != config.Piece.EMPTY:
                    break
                targetRowDirection, targetColDirection = targetRowDirection + i[0], targetColDirection + i[1]
        return False

    @staticmethod
    def king(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
        targetRow, targetCol = targetSquare
        directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] # All 8 possible king move directions
        for i in directions:
            targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
            if 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
                if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.KING and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
                    return True
        return False

def isSquareAttacked(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
    # Check for attacks
    if squareAttackChecking.pawn(board, targetSquare, attackingColour):
        return True
    if squareAttackChecking.bishop(board, targetSquare, attackingColour):
        return True
    if squareAttackChecking.knight(board, targetSquare, attackingColour):
        return True
    if squareAttackChecking.rook(board, targetSquare, attackingColour):
        return True
    if squareAttackChecking.queen(board, targetSquare, attackingColour):
        return True
    if squareAttackChecking.king(board, targetSquare, attackingColour):
        return True
    return False

def getLegalMovesForPiece(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
    sourcePiece, sourceColour = board.Board[row][col][0], board.Board[row][col][1]
    if sourcePiece == config.Piece.EMPTY:
        logger.error(msg = f"Board: Attempting to get legal moves for empty square {(row, col)}")
        return []
    if sourceColour != board.SideToMove:
        logger.error(msg = f"Board: Attempting to get legal moves for piece of colour {sourceColour.name} when it is {board.SideToMove.name}'s turn to move")
        return []
    pseudoLegalMoves: list[config.MoveData] = getPseudoLegalMovesForPiece(board, row, col)
    legalMoves: list[config.MoveData] = []
    for pseudoMove in pseudoLegalMoves:
        targetRow, targetCol, moveType = pseudoMove.toSquare[0], pseudoMove.toSquare[1], pseudoMove.moveType
        tempBoardHandling = BoardHandling()
        tempBoard: list[list[tuple[config.Piece, config.PieceColour]]] = []
        # Create the temporary board as a hard copy
        for i in board.Board:
            tempBoard.append(i.copy())
        tempBoardHandling.Board = tempBoard
        # Apply pseudo-legal move to the temporary board
        tempBoard[targetRow][targetCol] = tempBoard[row][col]
        tempBoard[row][col] = (config.Piece.EMPTY, config.PieceColour.WHITE)
        if moveType == config.MoveType.EN_PASSANT:
            if sourceColour == config.PieceColour.WHITE:
                tempBoard[targetRow + 1][targetCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
            else:
                tempBoard[targetRow - 1][targetCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
        # Check king check condition
        kingPosition: tuple[int, int] | tuple[Literal[-1], Literal[-1]] = findKing(tempBoardHandling, sourceColour)
        
        # Check whether the opponent is attacking the king
        kingInCheck: bool = False
        enemyColour: config.PieceColour
        if sourceColour == config.PieceColour.WHITE:
            enemyColour = config.PieceColour.BLACK
        else:
            enemyColour = config.PieceColour.WHITE
        kingInCheck = isSquareAttacked(tempBoardHandling, kingPosition, enemyColour)
        if not kingInCheck:
            legalMoves.append(pseudoMove)
    return legalMoves

def completePromotion(board: BoardHandling, promotionPieceType: config.Piece) -> None:
    if board.pendingPromotion is None:
        logger.error(msg = "Board: Attempting to complete promotion when there is no pending promotion")
        return
    if promotionPieceType == config.Piece.KING or promotionPieceType == config.Piece.EMPTY:
        logger.error(msg = f"Board: Attempting to promote to invalid piece type {promotionPieceType}")
        return
    toRow, toCol, colour = board.pendingPromotion.toSquare[0], board.pendingPromotion.toSquare[1], board.pendingPromotion.colour
    board.Board[toRow][toCol] = (promotionPieceType, colour)
    board.pendingPromotion = None
    board.EnPassantTargettableSquare = (-1, -1)
    board.changeSideToMove()

def processMove(board: BoardHandling, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> None:
    fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
    if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
        return # If an empty move; we exit
    moves: list[config.MoveData] = getLegalMovesForPiece(board, row = fromRow, col = fromCol)
    pieceToMove, colourToMove = board.Board[fromRow][fromCol][0], board.Board[fromRow][fromCol][1]

    # Check whether the move to be processed is a pseudo-legal move
    moveType: config.MoveType | None = None
    for move in moves:
        moveRow, moveCol, moveMoveType = move.toSquare[0], move.toSquare[1], move.moveType
        if moveRow == toRow and moveCol == toCol:
            moveType = moveMoveType
            break
    if moveType is None:
        logger.warning(msg = f"Board: Rejecting invalid move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}")
        return
    logger.info(msg = f"Board: Processing move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")

    board.Board[toRow][toCol] = board.Board[fromRow][fromCol]
    board.Board[fromRow][fromCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)

    if moveType == config.MoveType.PROMOTION:
        board.pendingPromotion = config.PromotionData(fromSquare = fromSquare, toSquare = toSquare, moveType = config.MoveType.PROMOTION, colour = colourToMove)
        board.EnPassantTargettableSquare = (-1, -1)
        return

    # Begin other move type processing
    if moveType == config.MoveType.EN_PASSANT: # Handle en passant
        if colourToMove == config.PieceColour.WHITE:
            board.Board[toRow + 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
        else:
            board.Board[toRow - 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
    board.EnPassantTargettableSquare = (-1, -1) # Reset after every move
    if pieceToMove == config.Piece.PAWN: # Handle pawn logic (setting en passant squares)
        if (fromRow, fromCol) == (toRow + 2, toCol):
            board.EnPassantTargettableSquare = (toRow + 1, toCol)
        elif (fromRow, fromCol) == (toRow - 2, toCol):
            board.EnPassantTargettableSquare = (toRow - 1, toCol)
        else:
            board.EnPassantTargettableSquare = (-1, -1)

    board.changeSideToMove()
