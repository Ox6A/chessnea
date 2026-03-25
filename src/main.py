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
        self.draggedPiece = None
        self.draggedPieceFrom = None
        for i in range(8):  
            row = []
            for i1 in range(8):
                row.append(defaultPiece)  # Placeholder for pieces
            self.board.append(row)
        self.setDefaultBoard()
    
    def scalePieceImages(self, pieceType, size):
        piece, color = pieceType
        if color == WHITE:
            if piece == PAWN:
                return pygame.transform.smoothscale(self.whitePawn, (size, size))
            elif piece == ROOK:
                return pygame.transform.smoothscale(self.whiteRook, (size, size))
            elif piece == KNIGHT:
                return pygame.transform.smoothscale(self.whiteKnight, (size, size))
            elif piece == BISHOP:
                return pygame.transform.smoothscale(self.whiteBishop, (size, size))
            elif piece == QUEEN:
                return pygame.transform.smoothscale(self.whiteQueen, (size, size))
            elif piece == KING:
                return pygame.transform.smoothscale(self.whiteKing, (size, size))
        elif color == BLACK:
            if piece == PAWN:
                return pygame.transform.smoothscale(self.blackPawn, (size, size))
            elif piece == ROOK:
                return pygame.transform.smoothscale(self.blackRook, (size, size))
            elif piece == KNIGHT:
                return pygame.transform.smoothscale(self.blackKnight, (size, size))
            elif piece == BISHOP:
                return pygame.transform.smoothscale(self.blackBishop, (size, size))
            elif piece == QUEEN:
                return pygame.transform.smoothscale(self.blackQueen, (size, size))
            elif piece == KING:
                return pygame.transform.smoothscale(self.blackKing, (size, size))
        return None

    def convertMouseCoordinatesToBoardIndex(self, position, cellWidth):
        x, y = position
        col = x // cellWidth
        row = 7 - (y // cellWidth)  # Invert row index to match chessboard orientation
        if 0 <= row < 8 and 0 <= col < 8:
            return int(row), int(col)
        return None

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

    def drawBoard(self, screen, mousePosition) -> None:
        width, height = screen.get_size()
        cellWidth = min(width, height) // 8
        pawnSize = int(cellWidth * 0.8)

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
                        pawnRect = self.whitePawn.get_rect(center=squareRect.center)
                        screen.blit(self.whitePawn, pawnRect)
                        continue
                    elif piece[0] == ROOK:
                        rookRect = self.whiteRook.get_rect(center=squareRect.center)
                        screen.blit(self.whiteRook, rookRect)
                        continue
                    elif piece[0] == KNIGHT:
                        knightRect = self.whiteKnight.get_rect(center=squareRect.center)
                        screen.blit(self.whiteKnight, knightRect)
                        continue
                    elif piece[0] == BISHOP:
                        bishopRect = self.whiteBishop.get_rect(center=squareRect.center)
                        screen.blit(self.whiteBishop, bishopRect)
                        continue
                    elif piece[0] == QUEEN:
                        queenRect = self.whiteQueen.get_rect(center=squareRect.center)
                        screen.blit(self.whiteQueen, queenRect)
                        continue
                    elif piece[0] == KING:
                        kingRect = self.whiteKing.get_rect(center=squareRect.center)
                        screen.blit(self.whiteKing, kingRect)
                        continue
                elif piece[1] == BLACK:
                    if piece[0] == PAWN:
                        pawnRect = self.blackPawn.get_rect(center=squareRect.center)
                        screen.blit(self.blackPawn, pawnRect)
                        continue
                    elif piece[0] == ROOK:
                        rookRect = self.blackRook.get_rect(center=squareRect.center)
                        screen.blit(self.blackRook, rookRect)
                        continue
                    elif piece[0] == KNIGHT:
                        knightRect = self.blackKnight.get_rect(center=squareRect.center)
                        screen.blit(self.blackKnight, knightRect)
                        continue
                    elif piece[0] == BISHOP:
                        bishopRect = self.blackBishop.get_rect(center=squareRect.center)
                        screen.blit(self.blackBishop, bishopRect)
                        continue
                    elif piece[0] == QUEEN:
                        queenRect = self.blackQueen.get_rect(center=squareRect.center)
                        screen.blit(self.blackQueen, queenRect)
                        continue
                    elif piece[0] == KING:
                        kingRect = self.blackKing.get_rect(center=squareRect.center)
                        screen.blit(self.blackKing, kingRect)
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
        mousePosition = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.Button == 1:
                square = board.convertMouseCoordinatesToBoardIndex(mousePosition, min(screen.get_size()) // 8)
                if square is not None:
                    row, col = square
                    board.draggedPiece = board.board[row][col]
            elif event.type == pygame.MOUSEBUTTONUP and event.Button == 1:
                board.draggedPiece = None

        board.drawBoard(screen, mousePosition)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()  
