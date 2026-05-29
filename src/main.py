from os import environ
import pygame
from pathlib import Path
from enum import IntEnum, Enum

class Globals(Enum): # Store global constants for the entire project
    FPS = 60 # FPS limit (does not have to be heigher than 60 for a chess game, might revisit later)
    WIDTH = 600 # Window width
    HEIGHT = 600 # Window height
    HEIGHT_PER_SQUARE = HEIGHT // 8 # Height per square = total height / number of squares (8)
    WIDTH_PER_SQUARE = WIDTH // 8 # Width per square = total height / number of squares (8)
    STARTING_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # Example FEN string for a standard starting position in chess
    ACCEPTABLE_FEN_CHARS = ["r", "n", "b", "q", "k", "p", "R", "N", "B", "Q", "K", "P", "-", "w", "b", "1", "2", "3", "4", "5", "6", "7", "8"] # Simpler than a regex string for acceptable chars when parsing FEN

class Piece(IntEnum): # LUT for integer equivalence for chess pieces
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5
    EMPTY = 6 # Default piece type

class MoveType(IntEnum): # LUT for integer equivalence of possible chess move types
    NORMAL = 0
    CAPTURE = 1
    EN_PASSANT = 2
    CASTLING = 3
    PROMOTION = 4

class CastlingRights(IntEnum): # LUT for integer equivalence of side castling rights when parsing FEN strings
    WHITE_KINGSIDE = 0
    WHITE_QUEENSIDE = 1
    BLACK_KINGSIDE = 2
    BLACK_QUEENSIDE = 3

class PieceColour(IntEnum): # LUT for integer equivalence of chess piece colours
    WHITE = 0
    BLACK = 1

class RenderingColours(Enum): # Lichess (lichess.org) default colour scheme
    SQUARE_WHITE = (240, 217, 181)
    SQUARE_BLACK = (181, 136, 99)
    PIECE_PICKED_UP_BACKGROUND = (60, 200, 60, 128)
    PIECE_LEGAL_MOVE_BACKGROUND = (60, 200, 60, 128)

# Default empty square is given as (Piece.EMPTY, PieceColour.White)

class BoardHandling():
    def __init__(self)  -> None:
        self.Board: list[list[tuple[Piece, PieceColour]]] = [[(Piece.EMPTY, PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board
        self.SideToMove: PieceColour = PieceColour.WHITE # White is the default side to move (subject to parsed FEN position)
        self.CastlingRights: list[CastlingRights] = [CastlingRights.WHITE_KINGSIDE, CastlingRights.WHITE_QUEENSIDE, CastlingRights.BLACK_KINGSIDE, CastlingRights.BLACK_QUEENSIDE]
        self.EnPassantTargettableSquare: tuple[int, int] = (-1, -1) # Defines which square is attackable under en passant
        self.FiftyMoveCounter: int = 0 # Niche rule allowing a draw after 50 moves without a capture
        self.FullMoveCounter: int = 0 # Constant tracking for current move nr.
        self.sprites: list[list[pygame.Surface | None]] = self.loadSprites() # Load sprites from disk
        self.piecePickedUp: tuple[int, int] = (-1, -1) # Current piece picked up by the mouse cursor

    def processMove(self, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> None:
        fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
        if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
            return # If an empty move; we exit
        moves: list[tuple[int, int, MoveType]] = self.getPseudoLegalMovesForPiece(row = fromRow, col = fromCol)
        # Check whether the move to be processed is a pseudo-legal move
        if (toRow, toCol, MoveType.NORMAL) in moves or (toRow, toCol, MoveType.CAPTURE) in moves or (toRow, toCol, MoveType.EN_PASSANT) in moves or (toRow, toCol, MoveType.CASTLING) in moves or (toRow, toCol, MoveType.PROMOTION) in moves:
            moveType: MoveType = MoveType.NORMAL
            for move in moves: # Assign move type to move to be processed
                if move[0] == toRow and move[1] == toCol:
                    moveType = move[2]
                    break
            print(f"Board: Processing move from {fromSquare} to {toSquare} for piece {self.Board[fromRow][fromCol][0].name} {self.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")
            # Process the standard move
            self.Board[toRow][toCol] = self.Board[fromRow][fromCol]
            self.Board[fromRow][fromCol] = (Piece.EMPTY, PieceColour.WHITE)

        # Begin other move type processing
        if (toRow, toCol, MoveType.EN_PASSANT) in moves: # Handle en passant
            if self.Board[fromRow][fromCol][1] == PieceColour.WHITE:
                self.Board[toRow + 1][toCol] = (Piece.EMPTY, PieceColour.WHITE)
            else:
                self.Board[toRow - 1][toCol] = (Piece.EMPTY, PieceColour.WHITE)
        if self.Board[fromRow][fromCol][0] == Piece.PAWN: # Handle pawn logic (setting en passant squares)
            if (fromRow, fromCol) == (toRow + 2, toCol):
                self.EnPassantTargettableSquare = (toRow + 1, toCol)
            elif (fromRow, fromCol) == (toRow - 2, toCol):
                self.EnPassantTargettableSquare = (toRow - 1, toCol)
            else:
                self.EnPassantTargettableSquare = (-1, -1)

        if self.SideToMove == PieceColour.WHITE: # Handle switching side to move flag after each move is processed
            self.SideToMove = PieceColour.BLACK 
        else:
            self.SideToMove = PieceColour.WHITE

    def getPseudoLegalMovesForPiece(self, row: int, col: int) -> list[tuple[int, int, MoveType]]:
        # In order to get all legal moves, we get all pseudo-legal moves (ignoring check conditions)
        validMoves: list[tuple[int, int, MoveType]] = []
        if self.Board[row][col][0] == Piece.EMPTY: # Standard move
            return [(-1, -1, MoveType.NORMAL)]
        elif self.Board[row][col][0] == Piece.PAWN: # Handle pawn logic (NEED A REFACTOR)
            if self.Board[row][col][1] == PieceColour.WHITE:
                if row - 1 >= 0:
                    if self.Board[row - 1][col][0] == Piece.EMPTY:
                        if row == 6:
                            if self.Board[row - 2][col][0] == Piece.EMPTY:
                                validMoves.append((row - 1, col, MoveType.NORMAL))
                                validMoves.append((row - 2, col, MoveType.NORMAL))
                        else:
                            validMoves.append((row - 1, col, MoveType.NORMAL))
                if row - 1 >= 0 and col + 1 <= 7:
                    if (self.Board[row - 1][col + 1][0] != Piece.EMPTY and 
                        self.Board[row - 1][col + 1][0] != Piece.KING and 
                        self.Board[row - 1][col + 1][1] != self.Board[row][col][1]):
                        validMoves.append((row - 1, col + 1, MoveType.CAPTURE))
                    if (row - 1, col + 1) == self.EnPassantTargettableSquare and self.Board[row - 1][col + 1][0] == Piece.EMPTY:
                        validMoves.append((row - 1, col + 1, MoveType.EN_PASSANT))
                    #if (((row - 1, col + 1) == self.EnPassantTargettableSquare and
                        #(self.Board[row - 1][col + 1][1] != self.Board[row][col][1])) or
                        #(self.Board[row - 1][col + 1][0] == Piece.EMPTY)):
                        #validMoves.append((row - 1, col + 1, MoveType.EN_PASSANT))
                if row - 1 >= 0 and col - 1 >= 0:
                    if (self.Board[row - 1][col - 1][0] != Piece.EMPTY and 
                        self.Board[row - 1][col - 1][0] != Piece.KING and  
                        self.Board[row - 1][col - 1][1] != self.Board[row][col][1]):
                        validMoves.append((row - 1, col - 1, MoveType.CAPTURE))
                    if (row - 1, col - 1) == self.EnPassantTargettableSquare:
                        validMoves.append((row - 1, col - 1, MoveType.EN_PASSANT))
            else:
                if row + 1 <= 7:
                    if self.Board[row + 1][col][0] == Piece.EMPTY:
                        if row == 1:
                            if self.Board[row + 2][col][0] == Piece.EMPTY:
                                validMoves.append((row + 1, col, MoveType.NORMAL))
                                validMoves.append((row + 2, col, MoveType.NORMAL))
                        else:
                            validMoves.append((row + 1, col, MoveType.NORMAL))
                if row + 1 <= 7 and col + 1 <= 7:
                    if (self.Board[row + 1][col + 1][0] != Piece.EMPTY and 
                        self.Board[row + 1][col + 1][0] != Piece.KING and 
                        self.Board[row + 1][col + 1][1] != self.Board[row][col][1]):
                        validMoves.append((row + 1, col + 1, MoveType.CAPTURE))
                    if (row + 1, col + 1) == self.EnPassantTargettableSquare:
                        validMoves.append((row + 1, col + 1, MoveType.EN_PASSANT))
                if row + 1 <= 7 and col - 1 >= 0:
                    if (self.Board[row + 1][col - 1][0] != Piece.EMPTY and 
                        self.Board[row + 1][col - 1][0] != Piece.KING and 
                        self.Board[row + 1][col - 1][1] != self.Board[row][col][1]):
                        validMoves.append((row + 1, col - 1, MoveType.CAPTURE))
                    if (row + 1, col - 1) == self.EnPassantTargettableSquare:
                        validMoves.append((row + 1, col - 1, MoveType.EN_PASSANT))
            return validMoves
        return [(-1, -1, MoveType.NORMAL)]

    def parseFENCoordinatesToBoardCoordinates(self, file: str, rank: str) -> tuple[int, int]:
        # Convert FEN coordinates into our internal representation
        if file not in "abcdefgh" or rank not in "12345678":
            raise ValueError(f"BoardHandling: Invalid FEN: Invalid input square field: {file}{rank}")
        return (8 - int(rank), "abcdefgh".index(file))

    def importFEN(self, fen: str) -> None:
        # Parse a position given in FEN into our internal representation, as well as assigning values to necessary flags for game flow
        splitFEN: list[str] = fen.split(sep = " ")
        if len(splitFEN) != 6: raise ValueError(f"Invalid FEN: Expected 6 fields, got {len(splitFEN)}") # FEN field nr. check (erroneous data)

        # Assigning the different parts of the FEN string into separate variables.
        sideToMoveFEN, castlingRightsFEN, enPassantTargetSquareFEN, fiftyMoveCounterFEN, fullMoveCounterFEN = splitFEN[1], splitFEN[2], splitFEN[3], splitFEN[4], splitFEN[5]

        # Set side to move flag
        if sideToMoveFEN == "w":
            self.SideToMove = PieceColour.WHITE
        elif sideToMoveFEN == "b":
            self.SideToMove = PieceColour.BLACK
        else:
            raise ValueError(f"Invalid FEN: Invalid side to move field: {sideToMoveFEN}")
        
        # Set castling rights flag
        if castlingRightsFEN == "-":
            self.CastlingRights = []
        else:
            self.CastlingRights = []
            for char in castlingRightsFEN:
                if char == "K":
                    self.CastlingRights.append(CastlingRights.WHITE_KINGSIDE)
                elif char == "Q":
                    self.CastlingRights.append(CastlingRights.WHITE_QUEENSIDE)
                elif char == "k":
                    self.CastlingRights.append(CastlingRights.BLACK_KINGSIDE)
                elif char == "q":
                    self.CastlingRights.append(CastlingRights.BLACK_QUEENSIDE)
                else:
                    raise ValueError(f"Invalid FEN: Invalid castling rights field: {castlingRightsFEN}")
        
        # Set en passant target flag
        if enPassantTargetSquareFEN == "-":
            self.EnPassantTargettableSquare = (-1, -1)
        else:
            file: str = enPassantTargetSquareFEN[0]
            rank: str = enPassantTargetSquareFEN[1]
            self.EnPassantTargettableSquare = self.parseFENCoordinatesToBoardCoordinates(file, rank)
        try:
            self.FiftyMoveCounter = int(fiftyMoveCounterFEN)
            self.FullMoveCounter = int(fullMoveCounterFEN)
        except ValueError:
            raise ValueError(f"Invalid FEN: Invalid move counter(s): {fiftyMoveCounterFEN} {fullMoveCounterFEN}")
        
        # Parse FEN board position
        splitFENRanks: list[str] = splitFEN[0].split(sep = "/")
        if len(splitFENRanks) != 8: raise ValueError(f"Invalid FEN: Expected 8 ranks, got {len(splitFENRanks)}") # FEN position rank nr. check (erroneous data)

        emptyBoard: list[list[tuple[Piece, PieceColour]]] = [[(Piece.EMPTY, PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board for us to populate
        for rankIndex, ranks in enumerate(splitFENRanks):
            fileIndex: int = 0
            for piece in ranks:
                if piece not in Globals.ACCEPTABLE_FEN_CHARS.value:
                    raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
                if piece in "12345678":
                    for i in range(int(piece)):
                        emptyBoard[rankIndex][fileIndex + i] = (Piece.EMPTY, PieceColour.WHITE)
                    fileIndex += int(piece)
                else:
                    colour: PieceColour = PieceColour.WHITE
                    if piece.isupper(): # Check char capitalisation before checking for equivalence with internal representation (invalid data)
                        colour = PieceColour.WHITE
                    else:
                        colour = PieceColour.BLACK
                    pieceUpper: str = piece.upper()
                    pieceType: Piece = Piece.EMPTY
                    match pieceUpper: # Needs a recent version of Python (>Python 3.7?)
                        case "P":
                            pieceType = Piece.PAWN
                        case "N":
                            pieceType = Piece.KNIGHT
                        case "B":
                            pieceType = Piece.BISHOP
                        case "R":
                            pieceType = Piece.ROOK
                        case "Q":
                            pieceType = Piece.QUEEN
                        case "K":
                            pieceType = Piece.KING
                        case _:
                            raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
                    emptyBoard[rankIndex][fileIndex] = (pieceType, colour)
                    fileIndex += 1
        self.Board = emptyBoard

    def loadSprites(self) -> list[list[pygame.Surface | None]]:
        # Loads all the sprites needed for game board rendering from disk in .svg format for scaling
        sprites: list[list[pygame.Surface | None]] = [[None for _ in range(6)] for _ in range(2)] # Empty nested list for sprites of all chess pieces in all colours
        for colour in PieceColour:
            for piece in Piece:
                if piece != Piece.EMPTY:
                    filename: str = f"{colour.name.lower()[0]}{piece.name.upper()[0]}.svg" # Expected file name format
                    if piece.name.lower() == "knight":
                        filename = f"{colour.name.lower()[0]}N.svg"
                    try:
                        img: pygame.Surface = pygame.image.load_sized_svg(file = str(Path(__file__).resolve().parent.parent / "assets" / filename), size = (Globals.WIDTH_PER_SQUARE.value * 0.9, Globals.WIDTH_PER_SQUARE.value * 0.9)).convert_alpha() # Scaling and loading from disk
                    except (FileNotFoundError, pygame.error) as e: # Handle missing sprites
                        print(f"ERROR at Init: Failed to load sprite for {colour.name} {piece.name} from {filename}: {e}")
                    else:
                        print(f"Init: Loaded sprite for {colour.name} {piece.name} from {filename}")
                        sprites[colour.value][piece.value] = img
        for colour in PieceColour:
            for piece in Piece:
                if piece != Piece.EMPTY and sprites[colour.value][piece.value] is None: # Double check if sprites were loaded correctly
                    print(f"ERROR at Init: Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
                    raise ValueError(f"Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
        return sprites

    def getSquareUnderMousePosition(self) -> tuple[int, int] | None:
        # Converts absolute coordinates for the mouse position provided by Pygame into a internal board square
        mouseX, mouseY = pygame.mouse.get_pos()
        col: int = mouseX // Globals.WIDTH_PER_SQUARE.value
        row: int = mouseY // Globals.HEIGHT_PER_SQUARE.value
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        else:
            return None

class Rendering():
    # Handle all board rendering functions
    def __init__(self) -> None:
        self.font: pygame.font.Font = pygame.font.Font(filename = None, size = 18) # Initialise the font used for debugging methods at object init

    def drawBoardBackground(self, screen: pygame.Surface, board: BoardHandling) -> None:
        # Draw the coloured squares for the chess board
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                if (row + col) % 2 == 0:
                    colour = RenderingColours.SQUARE_WHITE.value
                else:
                    colour = RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(surface = screen, color = colour, rect = pygame.Rect(col * Globals.WIDTH_PER_SQUARE.value, row * Globals.HEIGHT_PER_SQUARE.value, Globals.WIDTH_PER_SQUARE.value, Globals.HEIGHT_PER_SQUARE.value))
    
    def debugRenderingMethod(self, board: BoardHandling, screen: pygame.Surface) -> None:
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                coordinates: tuple[int, int] = (col * (Globals.WIDTH_PER_SQUARE.value), row * (Globals.HEIGHT_PER_SQUARE.value))
                label: str = f"{row}{col}"
                textSurface: pygame.Surface = self.font.render(text = label, antialias = True, color = (0, 0, 0))
                _ = screen.blit(source = textSurface, dest = (coordinates[0], coordinates[1]))

    def renderBoard(self, screen: pygame.Surface, board: BoardHandling) -> None:
        sprite: pygame.Surface | None
        spriteRect: pygame.Rect
        pickedUpSprite: pygame.Surface | None = None
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                piece, colour = board.Board[row][col]
                if piece != Piece.EMPTY and board.piecePickedUp != (row, col):
                    sprite = board.sprites[colour.value][piece.value]
                    if sprite is None:
                        print(f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
                    squareRect: pygame.Rect = pygame.Rect(
                        col * Globals.WIDTH_PER_SQUARE.value,
                        row * Globals.HEIGHT_PER_SQUARE.value,
                        Globals.WIDTH_PER_SQUARE.value,
                        Globals.HEIGHT_PER_SQUARE.value,
                    )
                    spriteRect = sprite.get_rect(center=squareRect.center)
                    _ = screen.blit(source=sprite, dest=spriteRect)
                elif board.piecePickedUp == (row, col):
                    mouseX, mouseY = pygame.mouse.get_pos()
                    if piece == Piece.EMPTY:
                        continue
                    pickedUpSprite = board.sprites[colour.value][piece.value]
                    if pickedUpSprite is None:
                        print(f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
                    pieceBackgroundSurface: pygame.Surface = pygame.Surface((Globals.WIDTH_PER_SQUARE.value, Globals.HEIGHT_PER_SQUARE.value), pygame.SRCALPHA)
                    _ = pieceBackgroundSurface.fill(RenderingColours.PIECE_PICKED_UP_BACKGROUND.value)
                    _ = screen.blit(source = pieceBackgroundSurface, dest = (col * Globals.WIDTH_PER_SQUARE.value, row * Globals.HEIGHT_PER_SQUARE.value))
                    moveBackgroundSurface: pygame.Surface = pygame.Surface((Globals.WIDTH_PER_SQUARE.value, Globals.HEIGHT_PER_SQUARE.value), pygame.SRCALPHA)
                    _ = moveBackgroundSurface.fill(RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value)
                    moves: list[tuple[int, int, MoveType]] = board.getPseudoLegalMovesForPiece(row, col)
                    for move in moves:
                        moveRow, moveCol, _ = move
                        if moveRow == -1 and moveCol == -1: continue
                        _ = pygame.draw.circle(surface = screen, color = RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, center = (moveCol * Globals.WIDTH_PER_SQUARE.value + Globals.WIDTH_PER_SQUARE.value // 2, moveRow * Globals.HEIGHT_PER_SQUARE.value + Globals.HEIGHT_PER_SQUARE.value // 2), radius = Globals.WIDTH_PER_SQUARE.value // 8)
        if board.piecePickedUp != (-1, -1) and pickedUpSprite is not None:
            mouseX, mouseY = pygame.mouse.get_pos()
            spriteRect = pickedUpSprite.get_rect(center=(mouseX, mouseY))
            _ = screen.blit(source = pickedUpSprite, dest = spriteRect)

def main() -> None:
    environ["SDL_VSYNC"] = "1" # enable V-Sync
    _ = pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(size = (Globals.WIDTH.value, Globals.HEIGHT.value))
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    print("Init: Pygame initialised")
    board: BoardHandling = BoardHandling()
    renderThreadInstance: Rendering = Rendering()
    board.importFEN(fen = Globals.STARTING_POSITION_FEN.value)
    running: bool = True
    print("Init: Started!")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square: tuple[int, int] = board.getSquareUnderMousePosition() or (-1, -1)
                if square != (-1, -1):
                    if board.SideToMove == board.Board[square[0]][square[1]][1] and board.Board[square[0]][square[1]][0] != Piece.EMPTY:
                        board.piecePickedUp = square    
            elif event.type == pygame.MOUSEBUTTONUP:
                board.processMove(fromSquare = board.piecePickedUp, toSquare = board.getSquareUnderMousePosition() or (-1, -1))
                board.piecePickedUp = (-1, -1)
        renderThreadInstance.drawBoardBackground(screen, board)
        #renderThreadInstance.debugRenderingMethod(board, screen)
        renderThreadInstance.renderBoard(screen, board)
        pygame.display.flip()
        _ = clock.tick(Globals.FPS.value)

    print("Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()