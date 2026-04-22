import pygame
from time import sleep
from pathlib import Path
from enum import IntEnum, Enum

class Globals(Enum):
    WIDTH = 600
    HEIGHT = 600
    FPS = 60

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
        self.EnPassantTargettableSquare: list[int] = [1, 1]
        self.FiftyMoveCounter: int = 0
        self.FullMoveCounter: int = 0
        self.sprites: list[list[pygame.Surface | None]] = self.loadSprites()

    def parseFEN(self, fen: str) -> None:
        pass

    def loadSprites(self) -> list[list[pygame.Surface | None]]:
        sprites: list[list[pygame.Surface | None]] = [[None for _ in range(6)] for _ in range(2)]
        for colour in PieceColour:
            for piece in Piece:
                if piece != Piece.EMPTY:
                    filename: str = f"{colour.name.lower()[0]}{piece.name.upper()[0]}.svg"
                    try:
                        img: pygame.Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / filename)).convert_alpha()
                    except FileNotFoundError as e:
                        print(f"ERROR at Init: Failed to load sprite for {colour.name} {piece.name} from {filename}: {e}")
                    else:
                        print(f"Init: Loaded sprite for {colour.name} {piece.name} from {filename}")
                        sprites[colour.value][piece.value] = img
        for colour in PieceColour:
            for piece in Piece:
                if piece != Piece.EMPTY and sprites[colour.value][piece.value] == None:
                    print(f"ERROR at Init: Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
                    raise ValueError(f"Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
        return sprites

class RenderThread():
    def __init__(self) -> None:
        pass

    def drawBoardBackground(self, screen: pygame.Surface, Board: BoardHandling) -> None:
        for row in range(len(Board.Board)):
            for col in range(len(Board.Board[row])):
                if (row + col) % 2 == 0:
                    colour = RenderingColours.SQUARE_WHITE.value
                else:
                    colour = RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(screen, colour, (col * (Globals.WIDTH.value // 8), row * (Globals.HEIGHT.value // 8), Globals.WIDTH.value // 8, Globals.HEIGHT.value // 8))
        

def main() -> None:
    _ = pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(size=(Globals.WIDTH.value, Globals.HEIGHT.value))
    pygame.display.set_caption("Chess")
    print("Init: Pygame initialised")
    Board: BoardHandling = BoardHandling()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        RenderThread().drawBoardBackground(screen, Board)
        pygame.display.flip()
        sleep(1 / Globals.FPS.value)
    print("Exiting...")
    pygame.quit()
if __name__ == "__main__":
    main()