import pygame
from pathlib import Path
from enum import IntEnum, Enum

class Globals(Enum):
    WIDTH = 600
    HEIGHT = 600
    WIDTH_PER_SQUARE = WIDTH // 8
    HEIGHT_PER_SQUARE = HEIGHT // 8
    FPS = 60
    STARTING_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    ACCEPTABLE_FEN_CHARS = ["r", "n", "b", "q", "k", "p", "R", "N", "B", "Q", "K", "P", "-", "w", "b", "1", "2", "3", "4", "5", "6", "7", "8"]

class Piece(IntEnum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5
    EMPTY = 6

class CastlingRights(IntEnum):
    WHITE_KINGSIDE = 0
    WHITE_QUEENSIDE = 1
    BLACK_KINGSIDE = 2
    BLACK_QUEENSIDE = 3

class PieceColour(IntEnum):
    WHITE = 0
    BLACK = 1

class RenderingColours(Enum):
    SQUARE_WHITE = (240, 217, 181)
    SQUARE_BLACK = (181, 136, 99)

class BoardHandling():
    def __init__(self)  -> None:
        self.Board: list[list[tuple[Piece, PieceColour]]] = [[(Piece.EMPTY, PieceColour.WHITE) for _ in range(8)] for _ in range(8)]
        self.SideToMove: PieceColour = PieceColour.WHITE
        self.CastlingRights: list[CastlingRights] = [CastlingRights.WHITE_KINGSIDE, CastlingRights.WHITE_QUEENSIDE, CastlingRights.BLACK_KINGSIDE, CastlingRights.BLACK_QUEENSIDE]
        self.EnPassantTargettableSquare: list[int] = [-1, -1]
        self.FiftyMoveCounter: int = 0
        self.FullMoveCounter: int = 0
        self.sprites: list[list[pygame.Surface | None]] = self.loadSprites()

    def parseFENCoordinatesToBoardCoordinates(self, file: str, rank: str) -> tuple[int, int]:
        if file not in "abcdefgh" or rank not in "12345678":
            raise ValueError(f"BoardHandling: Invalid FEN: Invalid input square field: {file}{rank}")
        return (8 - int(rank), "abcdefgh".index(file))

    def importFEN(self, fen: str) -> None:
        splitFEN: list[str] = fen.split(sep = " ")
        if len(splitFEN) != 6: raise ValueError(f"Invalid FEN: Expected 6 fields, got {len(splitFEN)}")

        sideToMoveFEN, castlingRightsFEN, enPassantTargetSquareFEN, fiftyMoveCounterFEN, fullMoveCounterFEN = splitFEN[1], splitFEN[2], splitFEN[3], splitFEN[4], splitFEN[5]
        if sideToMoveFEN == "w":
            self.SideToMove = PieceColour.WHITE
        elif sideToMoveFEN == "b":
            self.SideToMove = PieceColour.BLACK
        else:
            raise ValueError(f"Invalid FEN: Invalid side to move field: {sideToMoveFEN}")
        
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
        
        if enPassantTargetSquareFEN == "-":
            self.EnPassantTargettableSquare = [-1, -1]
        else:
            file: str = enPassantTargetSquareFEN[0]
            rank: str = enPassantTargetSquareFEN[1]
            self.EnPassantTargettableSquare = list[int](self.parseFENCoordinatesToBoardCoordinates(file, rank))
        try:
            self.FiftyMoveCounter = int(fiftyMoveCounterFEN)
            self.FullMoveCounter = int(fullMoveCounterFEN)
        except ValueError:
            raise ValueError(f"Invalid FEN: Invalid move counter(s): {fiftyMoveCounterFEN} {fullMoveCounterFEN}")
            
        splitFENRanks: list[str] = splitFEN[0].split(sep = "/")
        if len(splitFENRanks) != 8: raise ValueError(f"Invalid FEN: Expected 8 ranks, got {len(splitFENRanks)}")

        emptyBoard: list[list[tuple[Piece, PieceColour]]] = [[(Piece.EMPTY, PieceColour.WHITE) for _ in range(8)] for _ in range(8)]
        for rankIndex, ranks in enumerate[str](splitFENRanks):
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
                    if piece.isupper():
                        colour = PieceColour.WHITE
                    else:
                        colour = PieceColour.BLACK
                    pieceUpper: str = piece.upper()
                    pieceType: Piece = Piece.EMPTY
                    match pieceUpper:
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
        sprites: list[list[pygame.Surface | None]] = [[None for _ in range(6)] for _ in range(2)]
        for colour in PieceColour:
            for piece in Piece:
                if piece != Piece.EMPTY:
                    filename: str = f"{colour.name.lower()[0]}{piece.name.upper()[0]}.svg"
                    if piece.name.lower() == "knight":
                        filename = f"{colour.name.lower()[0]}N.svg"
                    try:
                        img: pygame.Surface = pygame.image.load_sized_svg(file = str(Path(__file__).resolve().parent.parent / "assets" / filename), size = (Globals.WIDTH_PER_SQUARE.value * 0.9, Globals.WIDTH_PER_SQUARE.value * 0.9)).convert_alpha()
                    except (FileNotFoundError, pygame.error) as e:
                        print(f"ERROR at Init: Failed to load sprite for {colour.name} {piece.name} from {filename}: {e}")
                    else:
                        print(f"Init: Loaded sprite for {colour.name} {piece.name} from {filename}")
                        sprites[colour.value][piece.value] = img
        for colour in PieceColour:
            for piece in Piece:
                if piece != Piece.EMPTY and sprites[colour.value][piece.value] is None:
                    print(f"ERROR at Init: Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
                    raise ValueError(f"Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
        return sprites

class RenderThread():
    def __init__(self) -> None:
        pass

    def drawBoardBackground(self, screen: pygame.Surface, board: BoardHandling) -> None:
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
                font: pygame.font.Font = pygame.font.Font(filename = None, size = 18)
                label: str = f"{row}{col}"
                textSurface: pygame.Surface = font.render(text = label, antialias = True, color = (0, 0, 0))
                _ = screen.blit(source = textSurface, dest = (coordinates[0], coordinates[1]))

    def renderBoard(self, screen: pygame.Surface, board: BoardHandling) -> None:
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                piece, colour = board.Board[row][col]
                if piece != Piece.EMPTY:
                    sprite: pygame.Surface | None = board.sprites[colour.value][piece.value]
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

def main() -> None:
    _ = pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(size = (Globals.WIDTH.value, Globals.HEIGHT.value))
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    print("Init: Pygame initialised")
    board: BoardHandling = BoardHandling()
    renderThreadInstance: RenderThread = RenderThread()
    board.importFEN(fen = Globals.STARTING_POSITION_FEN.value)
    running: bool = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        renderThreadInstance.drawBoardBackground(screen, board)
        #renderThreadInstance.debugRenderingMethod(board, screen)
        renderThreadInstance.renderBoard(screen, board)
        pygame.display.flip()
        _ = clock.tick(Globals.FPS.value)

    print("Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()