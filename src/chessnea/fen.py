import logging
import chessnea.config as config
import chessnea.board as boardHandling

logger: logging.Logger = logging.getLogger(__name__)

def parseFENCoordinatesToBoardCoordinates(file: str, rank: str) -> tuple[int, int]:
    # Convert FEN coordinates into our internal representation
    if file not in "abcdefgh" or rank not in "12345678":
        raise ValueError(f"BoardHandling: Invalid FEN: Invalid input square field: {file}{rank}")
    return (8 - int(rank), "abcdefgh".index(file))

def importFEN(board: boardHandling.BoardHandling, fen: str) -> None:
    # Parse a position given in FEN into our internal representation, as well as assigning values to necessary flags for game flow
    logger.info(msg = f"FEN: Importing FEN string: {fen}")
    splitFEN: list[str] = fen.split(sep = " ")
    if len(splitFEN) != 6: 
        raise ValueError(f"Invalid FEN: Expected 6 fields, got {len(splitFEN)}") # FEN field nr. check (erroneous data)

    # Assigning the different parts of the FEN string into separate variables.
    sideToMoveFEN, castlingRightsFEN, enPassantTargetSquareFEN, fiftyMoveCounterFEN, fullMoveCounterFEN = splitFEN[1], splitFEN[2], splitFEN[3], splitFEN[4], splitFEN[5]

    # Set side to move flag
    if sideToMoveFEN == "w":
        board.SideToMove = config.PieceColour.WHITE
    elif sideToMoveFEN == "b":
        board.SideToMove = config.PieceColour.BLACK
    else:
        raise ValueError(f"Invalid FEN: Invalid side to move field: {sideToMoveFEN}")
    
    # Set castling rights flag
    tempCastlingRights: list[config.CastlingRights] = []
    if castlingRightsFEN != "-":
        for char in castlingRightsFEN:
            if char == "K":
                tempCastlingRights.append(config.CastlingRights.WHITE_KINGSIDE)
            elif char == "Q":
                tempCastlingRights.append(config.CastlingRights.WHITE_QUEENSIDE)
            elif char == "k":
                tempCastlingRights.append(config.CastlingRights.BLACK_KINGSIDE)
            elif char == "q":
                tempCastlingRights.append(config.CastlingRights.BLACK_QUEENSIDE)
            else:
                raise ValueError(f"Invalid FEN: Invalid castling rights field: {castlingRightsFEN}")
    board.CastlingRights = tempCastlingRights
    
    # Set en passant target flag
    if enPassantTargetSquareFEN == "-":
        board.EnPassantTargettableSquare = (-1, -1)
    else:
        file: str = enPassantTargetSquareFEN[0]
        rank: str = enPassantTargetSquareFEN[1]
        board.EnPassantTargettableSquare = parseFENCoordinatesToBoardCoordinates(file, rank)
    try:
        board.FiftyMoveCounter = int(fiftyMoveCounterFEN)
        board.FullMoveCounter = int(fullMoveCounterFEN)
    except ValueError:
        raise ValueError(f"Invalid FEN: Invalid move counter(s): {fiftyMoveCounterFEN} {fullMoveCounterFEN}")
    
    # Parse FEN board position
    splitFENRanks: list[str] = splitFEN[0].split(sep = "/")
    if len(splitFENRanks) != 8: raise ValueError(f"Invalid FEN: Expected 8 ranks, got {len(splitFENRanks)}") # FEN position rank nr. check (erroneous data)

    emptyBoard: list[list[tuple[config.Piece, config.PieceColour]]] = [[(config.Piece.EMPTY, config.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board for us to populate
    for rankIndex, ranks in enumerate(splitFENRanks):
        fileIndex: int = 0
        for piece in ranks:
            if piece not in config.FEN_VALID_BOARD_CHARACTERS:
                raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
            if piece in "12345678":
                for i in range(int(piece)):
                    emptyBoard[rankIndex][fileIndex + i] = (config.Piece.EMPTY, config.PieceColour.WHITE)
                fileIndex += int(piece)
            else:
                colour: config.PieceColour = config.PieceColour.WHITE
                if piece.isupper(): # Check char capitalisation before checking for equivalence with internal representation (invalid data)
                    colour = config.PieceColour.WHITE
                else:
                    colour = config.PieceColour.BLACK
                pieceUpper: str = piece.upper()
                pieceType: config.Piece = config.Piece.EMPTY
                match pieceUpper: # Needs a recent version of Python (>Python 3.7?)
                    case "P":
                        pieceType = config.Piece.PAWN
                    case "N":
                        pieceType = config.Piece.KNIGHT
                    case "B":
                        pieceType = config.Piece.BISHOP
                    case "R":
                        pieceType = config.Piece.ROOK
                    case "Q":
                        pieceType = config.Piece.QUEEN
                    case "K":
                        pieceType = config.Piece.KING
                    case _:
                        raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
                emptyBoard[rankIndex][fileIndex] = (pieceType, colour)
                fileIndex += 1
    logger.info(msg = f"FEN: Successfully parsed FEN string, side to move: {board.SideToMove.name}, full-move counter: {board.FullMoveCounter}")
    board.Board = emptyBoard