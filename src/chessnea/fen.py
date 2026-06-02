from typing import Protocol
import chessnea.config as config
import chessnea.enums as enums

class BoardTypes(Protocol):
    Board: list[list[tuple[enums.Piece, enums.PieceColour]]]
    SideToMove: enums.PieceColour
    CastlingRights: list[enums.CastlingRights]
    EnPassantTargettableSquare: tuple[int, int]
    FiftyMoveCounter: int
    FullMoveCounter: int

def parseFENCoordinatesToBoardCoordinates(file: str, rank: str) -> tuple[int, int]:
    # Convert FEN coordinates into our internal representation
    if file not in "abcdefgh" or rank not in "12345678":
        raise ValueError(f"BoardHandling: Invalid FEN: Invalid input square field: {file}{rank}")
    return (8 - int(rank), "abcdefgh".index(file))

def importFEN(board: BoardTypes, fen: str) -> None:
    # Parse a position given in FEN into our internal representation, as well as assigning values to necessary flags for game flow
    splitFEN: list[str] = fen.split(sep = " ")
    if len(splitFEN) != 6: 
        raise ValueError(f"Invalid FEN: Expected 6 fields, got {len(splitFEN)}") # FEN field nr. check (erroneous data)

    # Assigning the different parts of the FEN string into separate variables.
    sideToMoveFEN, castlingRightsFEN, enPassantTargetSquareFEN, fiftyMoveCounterFEN, fullMoveCounterFEN = splitFEN[1], splitFEN[2], splitFEN[3], splitFEN[4], splitFEN[5]

    # Set side to move flag
    if sideToMoveFEN == "w":
        board.SideToMove = enums.PieceColour.WHITE
    elif sideToMoveFEN == "b":
        board.SideToMove = enums.PieceColour.BLACK
    else:
        raise ValueError(f"Invalid FEN: Invalid side to move field: {sideToMoveFEN}")
    
    # Set castling rights flag
    if castlingRightsFEN == "-":
        board.CastlingRights = []
    else:
        board.CastlingRights = []
        for char in castlingRightsFEN:
            if char == "K":
                board.CastlingRights.append(enums.CastlingRights.WHITE_KINGSIDE)
            elif char == "Q":
                board.CastlingRights.append(enums.CastlingRights.WHITE_QUEENSIDE)
            elif char == "k":
                board.CastlingRights.append(enums.CastlingRights.BLACK_KINGSIDE)
            elif char == "q":
                board.CastlingRights.append(enums.CastlingRights.BLACK_QUEENSIDE)
            else:
                raise ValueError(f"Invalid FEN: Invalid castling rights field: {castlingRightsFEN}")
    
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

    emptyBoard: list[list[tuple[enums.Piece, enums.PieceColour]]] = [[(enums.Piece.EMPTY, enums.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board for us to populate
    for rankIndex, ranks in enumerate(splitFENRanks):
        fileIndex: int = 0
        for piece in ranks:
            if piece not in config.FEN_VALID_BOARD_CHARACTERS:
                raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
            if piece in "12345678":
                for i in range(int(piece)):
                    emptyBoard[rankIndex][fileIndex + i] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)
                fileIndex += int(piece)
            else:
                colour: enums.PieceColour = enums.PieceColour.WHITE
                if piece.isupper(): # Check char capitalisation before checking for equivalence with internal representation (invalid data)
                    colour = enums.PieceColour.WHITE
                else:
                    colour = enums.PieceColour.BLACK
                pieceUpper: str = piece.upper()
                pieceType: enums.Piece = enums.Piece.EMPTY
                match pieceUpper: # Needs a recent version of Python (>Python 3.7?)
                    case "P":
                        pieceType = enums.Piece.PAWN
                    case "N":
                        pieceType = enums.Piece.KNIGHT
                    case "B":
                        pieceType = enums.Piece.BISHOP
                    case "R":
                        pieceType = enums.Piece.ROOK
                    case "Q":
                        pieceType = enums.Piece.QUEEN
                    case "K":
                        pieceType = enums.Piece.KING
                    case _:
                        raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
                emptyBoard[rankIndex][fileIndex] = (pieceType, colour)
                fileIndex += 1
    board.Board = emptyBoard