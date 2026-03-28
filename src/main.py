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
DISPLAY_INDEX = False

class Board:
    def __init__(self): 
        defaultPiece = [PAWN, WHITE]
        self.sideToMove: int = WHITE
        self.targetsVulnerableToEnPassant: list[list[int]] = []
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

        self.board: list[list[list[int | None]]] = []
        self.draggedPiece: list[int | None] = []
        self.draggedPieceFrom: list[int] = [] 
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
        pieceSize = int(cellWidth * 0.9)

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
                pieceImage = self.scalePieceImages(piece, pieceSize)
                piecePickedUpBackground = pygame.Surface((cellWidth, cellWidth), pygame.SRCALPHA)
                if pieceImage is not None:
                    if [boardRow, boardCol] != self.draggedPieceFrom:
                        pieceRect = pieceImage.get_rect(center=squareRect.center)
                        screen.blit(pieceImage, pieceRect)
                        continue
                    else:
                        pieceRect = pieceImage.get_rect(center=squareRect.center)
                        pieceImage.set_alpha(128)  # Make the piece semi-transparent
                        _ = piecePickedUpBackground.fill((60, 200, 60, 128))
                        screen.blit(piecePickedUpBackground, squareRect)
                        screen.blit(pieceImage, pieceRect)
                if DISPLAY_INDEX:
                    index = boardRow * 8 + boardCol
                    text = font.render(str(index), True, (0, 0, 0))
                    textRect = text.get_rect(center=squareRect.center)
                    screen.blit(text, textRect)
                #print(f"{mousePosition}, {self.draggedPiece}, {self.draggedPieceFrom}, {boardRow}, {boardCol}")
        if mousePosition is not None and self.draggedPiece and self.draggedPieceFrom:
            row = int(self.draggedPieceFrom[0])
            col = int(self.draggedPieceFrom[1])
            piece = self.board[row][col]
            legalMoves = self.checkLegalMoves(self.draggedPieceFrom)
            circleRadius = max(4, cellWidth // 8)
            for i in legalMoves:
                legalMoveCenter = (i[1] * cellWidth + cellWidth // 2, (7 - i[0]) * cellWidth + cellWidth // 2)
                _ = pygame.draw.circle(screen, (60, 200, 60, 128), legalMoveCenter, circleRadius)
            currentSquare: tuple[int, int] | None = self.convertMouseCoordinatesToBoardIndex(mousePosition[1], min(screen.get_size()) // 8)
            if currentSquare != tuple(self.draggedPieceFrom):
                _ = piecePickedUpBackground.fill((60, 200, 60, 64))
                screen.blit(piecePickedUpBackground, pygame.Rect(currentSquare[1] * cellWidth, (7 - currentSquare[0]) * cellWidth, cellWidth, cellWidth))
            draggedPieceImage = self.scalePieceImages(piece, pieceSize)
            if draggedPieceImage is not None:
                draggedPieceRect = draggedPieceImage.get_rect(center=mousePosition[1])
                screen.blit(draggedPieceImage, draggedPieceRect)
    
    def checkLegalMoves(self, fromSquare) -> list[list[int]]:
        validMoves = []
        piece = self.board[fromSquare[0]][fromSquare[1]]
        if piece[0] == PAWN:
            direction = 1 if piece[1] == WHITE else -1
            nextRow = fromSquare[0] + direction
            if 0 <= nextRow < 8: # Move forward
                if self.board[nextRow][fromSquare[1]][0] == EMPTY:
                    validMoves.append([nextRow, fromSquare[1], False])
            else:
                return validMoves
            if (piece[1] == WHITE and fromSquare[0] == 1) or (piece[1] == BLACK and fromSquare[0] == 6): # Moves 2 squares forward from starting position 
                nextRow = fromSquare[0] + 2 * direction
                if 0 <= nextRow < 8:
                    if self.board[nextRow][fromSquare[1]][0] == EMPTY and self.board[fromSquare[0] + direction][fromSquare[1]][0] == EMPTY:
                        validMoves.append([nextRow, fromSquare[1], False])
            captureRow = fromSquare[0] + direction
            if 0 <= captureRow < 8: # Capture moves (diagonal)
                rightCol = fromSquare[1] + 1
                leftCol = fromSquare[1] - 1
                if rightCol < 8 and self.board[captureRow][rightCol][0] != EMPTY and self.board[captureRow][rightCol][1] != piece[1]:
                    validMoves.append([captureRow, rightCol, True])
                if leftCol >= 0 and self.board[captureRow][leftCol][0] != EMPTY and self.board[captureRow][leftCol][1] != piece[1]:
                    validMoves.append([captureRow, leftCol, True])

                # En passant capture moves
                if rightCol < 8 and [fromSquare[0], rightCol] in self.targetsVulnerableToEnPassant:
                    if self.board[fromSquare[0]][rightCol][0] == PAWN and self.board[fromSquare[0]][rightCol][1] != piece[1] and self.board[captureRow][rightCol][0] == EMPTY:
                        validMoves.append([captureRow, rightCol, True])
                if leftCol >= 0 and [fromSquare[0], leftCol] in self.targetsVulnerableToEnPassant:
                    if self.board[fromSquare[0]][leftCol][0] == PAWN and self.board[fromSquare[0]][leftCol][1] != piece[1] and self.board[captureRow][leftCol][0] == EMPTY:
                        validMoves.append([captureRow, leftCol, True])

        return validMoves

    def registerNewPiecePosition(self, fromSquare, toSquare, piece) -> None:
        if self.board[toSquare[0]][toSquare[1]][0] == EMPTY:
            self.board[toSquare[0]][toSquare[1]] = piece
            self.board[fromSquare[0]][fromSquare[1]] = [EMPTY, None]

def main():
    _ = pygame.init()
    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("Chess")
    board = Board()

    sentMousePosition = None
    running = True
    while running:
        mousePosition = pygame.mouse.get_pos()
        if board.draggedPiece:
            sentMousePosition = mousePosition
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = board.convertMouseCoordinatesToBoardIndex(mousePosition, min(screen.get_size()) // 8)
                if square is not None:
                    row, col = square
                    board.draggedPiece = board.board[row][col]
                    board.draggedPieceFrom = [row, col]
                    sentMousePosition = mousePosition
            elif event.type == pygame.MOUSEBUTTONUP:
                if board.draggedPiece:
                    fromSquare = board.draggedPieceFrom
                    toSquare = board.convertMouseCoordinatesToBoardIndex(mousePosition, min(screen.get_size()) // 8)
                    #print(f"Attempting to move piece from {fromSquare} to {toSquare}")
                    legalMoves = board.checkLegalMoves(fromSquare)
                    for legalMove in legalMoves:
                        legalMoveLocation: list[int] = [legalMove[0], legalMove[1]]
                        if toSquare is not None and list(toSquare) == legalMoveLocation:
                            if toSquare[0] - 2 == fromSquare[0] or toSquare[0] + 2 == fromSquare[0]: # If the move is a 2-square pawn move, add the square behind the pawn to the list of squares vulnerable to en passant
                                board.targetsVulnerableToEnPassant.append([toSquare[0], toSquare[1]])
                            if legalMove[2]:  # If the move is a capture, remove the captured piece
                                if board.board[toSquare[0]][toSquare[1]][0] == EMPTY: # If the target square is empty, it must be an en passant capture
                                    if board.draggedPiece[1] == WHITE:
                                        board.board[toSquare[0] - 1][toSquare[1]] = [EMPTY, None]
                                    else:
                                        board.board[toSquare[0] + 1][toSquare[1]] = [EMPTY, None]
                                else:
                                    board.board[toSquare[0]][toSquare[1]] = [EMPTY, None]
                            board.registerNewPiecePosition(fromSquare, toSquare, board.draggedPiece)
                            break
                board.draggedPiece = []
                board.draggedPieceFrom = []
                sentMousePosition = None
        dragging = [True, sentMousePosition]
        board.drawBoard(screen, dragging)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()  
