import logging

import chessnea.fen as fen
import chessnea.board as boardHandling
import chessnea.config as config

logger: logging.Logger = logging.getLogger(name = __name__)

def getDisambiguation(position: config.MoveHistoryData, previousPosition: config.MoveHistoryData) -> str:
    if position.piece == config.Piece.PAWN or position.piece == config.Piece.KING:
        return ""
    move: config.MoveData | None = position.move
    if move is None:
        logger.error(msg = "PGN: Invalid move in position history, panicking. (Move is None)")
        raise ValueError("PGN: Invalid move in position history, panicking. (Move is None)")
    tempBoard: boardHandling.BoardHandling = boardHandling.BoardHandling()
    fen.importFEN(board = tempBoard, fen = previousPosition.fen)
    disambiguationPos: list[tuple[int, int]] = []
    for rowIndex, row in enumerate[list[tuple[config.Piece, config.PieceColour]]](tempBoard.Board):
        for colIndex, col in enumerate[tuple[config.Piece, config.PieceColour]](row):
            if col[0] == position.piece:
                if col[1] == position.colour:
                    disambiguationPos.append((rowIndex, colIndex))
    if (move.fromSquare) in disambiguationPos:
        disambiguationPos.remove((move.fromSquare))
    disambiguationMoveLegal: list[config.MoveData] = []

    # Get legal moves
    legalMoves: list[config.MoveData] = []
    for dPosition in disambiguationPos:
        legalMoves = boardHandling.getLegalMovesForPiece(board = tempBoard, row = dPosition[0], col = dPosition[1])
        for moveLegal in legalMoves:
            if moveLegal.toSquare == move.toSquare:
                disambiguationMoveLegal.append(moveLegal)

    if disambiguationMoveLegal == []:
        return ""

    sameFileExists: bool = False
    sameRankExists: bool = False
    for moveLegal in disambiguationMoveLegal:
        if moveLegal.fromSquare[1] == move.fromSquare[1]:
            sameFileExists = True
        if moveLegal.fromSquare[0] == move.fromSquare[0]:
            sameRankExists = True

    if not sameFileExists:
        # Same file
        return config.InternalToAlgebraic.FILE[move.fromSquare[1]]
    if not sameRankExists:
        # Same rank
        return config.InternalToAlgebraic.RANK[move.fromSquare[0]]
    return config.InternalToAlgebraic.FILE[move.fromSquare[1]] + config.InternalToAlgebraic.RANK[move.fromSquare[0]]

def getCastling(position: config.MoveHistoryData) -> str:
    move: config.MoveData | None = position.move
    if move is None:
        logger.error(msg = "PGN: Invalid move in position history, panicking. (Move is None)")
        raise ValueError("PGN: Invalid move in position history, panicking. (Move is None)")
    if move.moveType != config.MoveType.CASTLING:
        return ""
    if position.piece != config.Piece.KING:
        logger.error(msg = "PGN: Invalid move in position history, panicking. (Attempted castling with a non-king piece!)")
        raise ValueError("PGN: Invalid move in position history, panicking. (Attempted castling with a non-king piece!)")
    if move.toSquare[1] == 6:
        return "O-O"
    if move.toSquare[1] == 2:
        return "O-O-O"
    logger.error(msg = f"PGN: Invalid castling target square: {move.toSquare}")
    raise ValueError(f"PGN: Invalid castling target square: {move.toSquare}")

def getCheckmate(position: config.MoveHistoryData) -> str:
    if not position.checkState.inCheck:
        return ""
    tempBoard: boardHandling.BoardHandling = boardHandling.BoardHandling()
    fen.importFEN(board = tempBoard, fen = position.fen)

    legalMoves: list[config.MoveData] = boardHandling.getAllLegalMovesForSide(board = tempBoard, colour = tempBoard.SideToMove)

    if legalMoves == []:
        return "#"
    else:
        return "+"

def convertPositionHistoryToPGN(board: boardHandling.BoardHandling) -> str:
    # Order: Move Nr, Castling, Piece, Disambiguation, 
    # Pawn capture source file, Capture marker, Destination square,
    # Promotion, Check/checkmate
    stringPGN: str = ""
    fullMoveCounter: int = 0
    previousPosition: config.MoveHistoryData = board.PositionHistory[0]
    for positionIndex, position in enumerate[config.MoveHistoryData](board.PositionHistory):
        if positionIndex == 0:
            continue
        if position.colour == config.PieceColour.WHITE:
            # Move Nr
            fullMoveCounter += 1
            stringPGN += f"{fullMoveCounter}. "
        previousPosition = board.PositionHistory[positionIndex - 1]
        halfMovePGN: str = ""
        move: config.MoveData | None = position.move
        if move is None:
            logger.error(msg = f"PGN: Invalid move in position history: {position.move}")
            raise ValueError
        # Castling
        castlingPGN: str = getCastling(position = position)
        if castlingPGN != "":
            halfMovePGN += castlingPGN
        else:
            # Piece
            halfMovePGN += config.PieceToPGN.PIECE[position.piece]

            # Disambiguation
            disambiguationPGN: str = getDisambiguation(position = position, previousPosition = previousPosition)
            halfMovePGN += disambiguationPGN

            # Capture
            isCapture: bool = position.capturedPiece != config.Piece.EMPTY or move.moveType == config.MoveType.EN_PASSANT
            if isCapture:
                # Pawn capture
                if position.piece == config.Piece.PAWN:
                    halfMovePGN += config.InternalToAlgebraic.FILE[move.fromSquare[1]]
                halfMovePGN += "x"

            # Destination
            halfMovePGN += f"{config.InternalToAlgebraic.FILE[move.toSquare[1]]}{config.InternalToAlgebraic.RANK[move.toSquare[0]]}"

            # Promotion
            if move.promotionPiece is not None:
                halfMovePGN += f"={config.PieceToPGN.PIECE[move.promotionPiece]}"

        # Check/checkmate
        checkPGN: str = getCheckmate(position = position)
        halfMovePGN += checkPGN
        stringPGN += halfMovePGN + " "
        previousPosition = position
    return stringPGN.strip()