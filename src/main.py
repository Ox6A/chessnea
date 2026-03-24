from typing import Any


import pygame
from pygame import Surface
from pathlib import Path
# pyright: reportUnusedVariable=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false

# Globals
DEFAULT_WIDTH, DEFAULT_HEIGHT = 600, 600
FPS = 60
EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 0, 1, 2, 3, 4, 5, 6
WHITE, BLACK = 0, 1

# Colours
SQUARE_WHITE = (240, 217, 181)
SQUARE_BLACK = (181, 136, 99)

# Variables
DISPLAY_INDEX = True

class Board:
    def __init__(self): 
        defaultPiece = [PAWN, WHITE]
        self.whitePawn: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "wP.svg")).convert_alpha()
        self.whiteRook: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "wR.svg")).convert_alpha()
        self.whiteKnight: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "wN.svg")).convert_alpha()
        self.whiteBishop: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "wB.svg")).convert_alpha()
        self.whiteQueen: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "wQ.svg")).convert_alpha()
        self.whiteKing: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "wK.svg")).convert_alpha()
        
        self.blackPawn: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "bP.svg")).convert_alpha()
        self.blackRook: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "bR.svg")).convert_alpha()
        self.blackKnight: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "bN.svg")).convert_alpha()
        self.blackBishop: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "bB.svg")).convert_alpha()
        self.blackQueen: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "bQ.svg")).convert_alpha()
        self.blackKing: Surface = pygame.image.load(str(Path(__file__).resolve().parent.parent / "assets" / "bK.svg")).convert_alpha()
        self.board: list[list[list[Any]]] = []
        for i in range(8):  
            row = []
            for i1 in range(8):
                row.append(defaultPiece)  # Placeholder for pieces
            self.board.append(row)
        self.setDefaultBoard()
    
    def setDefaultBoard(self):
        # Set up the default chess board with pieces in their starting positions
        self.board = [
            [[ROOK, WHITE], [KNIGHT, WHITE], [BISHOP, WHITE], [QUEEN, WHITE], [KING, WHITE], [BISHOP, WHITE], [KNIGHT, WHITE], [ROOK, WHITE]],
            [[PAWN, WHITE] for _ in range(8)],
            [[EMPTY, None] for _ in range(8)],
            [[EMPTY, None] for _ in range(8)],
            [[EMPTY, None] for _ in range(8)],
            [[EMPTY, None] for _ in range(8)],
            [[PAWN, BLACK] for _ in range(8)],
            [[ROOK, BLACK], [KNIGHT, BLACK], [BISHOP, BLACK], [QUEEN, BLACK], [KING, BLACK], [BISHOP, BLACK], [KNIGHT, BLACK], [ROOK, BLACK]],
    ]

    def drawBoard(self, screen) -> None:
        width, height = screen.get_size()
        cellWidth = min(width, height) // 8
        pawnSize = int(cellWidth * 0.8)
        whitePawn = pygame.transform.smoothscale(self.whitePawn, (pawnSize, pawnSize))
        whiteRook = pygame.transform.smoothscale(self.whiteRook, (pawnSize, pawnSize))
        whiteKnight = pygame.transform.smoothscale(self.whiteKnight, (pawnSize, pawnSize))
        whiteBishop = pygame.transform.smoothscale(self.whiteBishop, (pawnSize, pawnSize))
        whiteQueen = pygame.transform.smoothscale(self.whiteQueen, (pawnSize, pawnSize))
        whiteKing = pygame.transform.smoothscale(self.whiteKing, (pawnSize, pawnSize))

        blackPawn = pygame.transform.smoothscale(self.blackPawn, (pawnSize, pawnSize))
        blackRook = pygame.transform.smoothscale(self.blackRook, (pawnSize, pawnSize))
        blackKnight = pygame.transform.smoothscale(self.blackKnight, (pawnSize, pawnSize))
        blackBishop = pygame.transform.smoothscale(self.blackBishop, (pawnSize, pawnSize))
        blackQueen = pygame.transform.smoothscale(self.blackQueen, (pawnSize, pawnSize))
        blackKing = pygame.transform.smoothscale(self.blackKing, (pawnSize, pawnSize))

        font = pygame.font.SysFont(None, 36)

        screen.fill(SQUARE_WHITE)
        for boardRow, row in enumerate(self.board):
            screenRow = 7 - boardRow  # Invert row index to match chessboard orientation
            for boardCol, piece in enumerate(row):
                if (boardRow + boardCol) % 2 == 0:
                    color = SQUARE_BLACK
                else:
                    color = SQUARE_WHITE
                squareRect = pygame.draw.rect(screen, color, rect=(boardCol * cellWidth, screenRow * cellWidth, cellWidth, cellWidth))
                if piece[1] == WHITE:
                    if piece[0] == PAWN:
                        pawnRect = whitePawn.get_rect(center=squareRect.center)
                        screen.blit(whitePawn, pawnRect)
                        continue
                    elif piece[0] == ROOK:
                        rookRect = whiteRook.get_rect(center=squareRect.center)
                        screen.blit(whiteRook, rookRect)
                        continue
                    elif piece[0] == KNIGHT:
                        knightRect = whiteKnight.get_rect(center=squareRect.center)
                        screen.blit(whiteKnight, knightRect)
                        continue
                    elif piece[0] == BISHOP:
                        bishopRect = whiteBishop.get_rect(center=squareRect.center)
                        screen.blit(whiteBishop, bishopRect)
                        continue
                    elif piece[0] == QUEEN:
                        queenRect = whiteQueen.get_rect(center=squareRect.center)
                        screen.blit(whiteQueen, queenRect)
                        continue
                    elif piece[0] == KING:
                        kingRect = whiteKing.get_rect(center=squareRect.center)
                        screen.blit(whiteKing, kingRect)
                        continue
                elif piece[1] == BLACK:
                    if piece[0] == PAWN:
                        pawnRect = blackPawn.get_rect(center=squareRect.center)
                        screen.blit(blackPawn, pawnRect)
                        continue
                    elif piece[0] == ROOK:
                        rookRect = blackRook.get_rect(center=squareRect.center)
                        screen.blit(blackRook, rookRect)
                        continue
                    elif piece[0] == KNIGHT:
                        knightRect = blackKnight.get_rect(center=squareRect.center)
                        screen.blit(blackKnight, knightRect)
                        continue
                    elif piece[0] == BISHOP:
                        bishopRect = blackBishop.get_rect(center=squareRect.center)
                        screen.blit(blackBishop, bishopRect)
                        continue
                    elif piece[0] == QUEEN:
                        queenRect = blackQueen.get_rect(center=squareRect.center)
                        screen.blit(blackQueen, queenRect)
                        continue
                    elif piece[0] == KING:
                        kingRect = blackKing.get_rect(center=squareRect.center)
                        screen.blit(blackKing, kingRect)
                        continue

                if DISPLAY_INDEX:
                    index = boardRow * 8 + boardCol
                    text = font.render(str(index), True, (0, 0, 0))
                    textRect = text.get_rect(center=squareRect.center)
                    screen.blit(text, textRect)
        

def main():
    _ = pygame.init()
    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("Chess")
    board = Board()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        board.drawBoard(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()  
