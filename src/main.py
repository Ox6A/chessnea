from os import environ
import pygame

import chessnea.config as config
import chessnea.enums as enums
import chessnea.assets as assets
import chessnea.fen as fen
import chessnea.moves as moveHandling

class BoardHandling():
    def __init__(self)  -> None:
        self.Board: list[list[tuple[enums.Piece, enums.PieceColour]]] = [[(enums.Piece.EMPTY, enums.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board
        self.SideToMove: enums.PieceColour = enums.PieceColour.WHITE # White is the default side to move (subject to parsed FEN position)
        self.CastlingRights: list[enums.CastlingRights] = [enums.CastlingRights.WHITE_KINGSIDE, enums.CastlingRights.WHITE_QUEENSIDE, enums.CastlingRights.BLACK_KINGSIDE, enums.CastlingRights.BLACK_QUEENSIDE]
        self.EnPassantTargettableSquare: tuple[int, int] = (-1, -1) # Defines which square is attackable under en passant
        self.FiftyMoveCounter: int = 0 # Niche rule allowing a draw after 50 moves without a capture
        self.FullMoveCounter: int = 0 # Constant tracking for current move nr.
        self.sprites: list[list[pygame.Surface | None]] = assets.loadSprites() # Load sprites from disk
        self.piecePickedUp: tuple[int, int] = (-1, -1) # Current piece picked up by the mouse cursor

    def processMove(self, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> None:
        fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
        if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
            return # If an empty move; we exit
        moves: list[tuple[int, int, enums.MoveType]] = moveHandling.getPseudoLegalMovesForPiece(self, row = fromRow, col = fromCol)
        # Check whether the move to be processed is a pseudo-legal move
        if (toRow, toCol, enums.MoveType.NORMAL) in moves or (toRow, toCol, enums.MoveType.CAPTURE) in moves or (toRow, toCol, enums.MoveType.EN_PASSANT) in moves or (toRow, toCol, enums.MoveType.CASTLING) in moves or (toRow, toCol, enums.MoveType.PROMOTION) in moves:
            moveType: enums.MoveType = enums.MoveType.NORMAL
            for move in moves: # Assign move type to move to be processed
                if move[0] == toRow and move[1] == toCol:
                    moveType = move[2]
                    break
            print(f"Board: Processing move from {fromSquare} to {toSquare} for piece {self.Board[fromRow][fromCol][0].name} {self.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")
            # Process the standard move
            self.Board[toRow][toCol] = self.Board[fromRow][fromCol]
            self.Board[fromRow][fromCol] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)

        # Begin other move type processing
        if (toRow, toCol, enums.MoveType.EN_PASSANT) in moves: # Handle en passant
            if self.Board[fromRow][fromCol][1] == enums.PieceColour.WHITE:
                self.Board[toRow + 1][toCol] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)
            else:
                self.Board[toRow - 1][toCol] = (enums.Piece.EMPTY, enums.PieceColour.WHITE)
        if self.Board[fromRow][fromCol][0] == enums.Piece.PAWN: # Handle pawn logic (setting en passant squares)
            if (fromRow, fromCol) == (toRow + 2, toCol):
                self.EnPassantTargettableSquare = (toRow + 1, toCol)
            elif (fromRow, fromCol) == (toRow - 2, toCol):
                self.EnPassantTargettableSquare = (toRow - 1, toCol)
            else:
                self.EnPassantTargettableSquare = (-1, -1)

        if self.SideToMove == enums.PieceColour.WHITE: # Handle switching side to move flag after each move is processed
            self.SideToMove = enums.PieceColour.BLACK 
        else:
            self.SideToMove = enums.PieceColour.WHITE

    def getSquareUnderMousePosition(self) -> tuple[int, int] | None:
        # Converts absolute coordinates for the mouse position provided by Pygame into a internal board square
        mouseX, mouseY = pygame.mouse.get_pos()
        col: int = mouseX // config.WIDTH_PER_SQUARE
        row: int = mouseY // config.HEIGHT_PER_SQUARE
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
                    colour = enums.RenderingColours.SQUARE_WHITE.value
                else:
                    colour = enums.RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(surface = screen, color = colour, rect = pygame.Rect(col * config.WIDTH_PER_SQUARE, row * config.HEIGHT_PER_SQUARE, config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE))
    
    def debugRenderingMethod(self, board: BoardHandling, screen: pygame.Surface) -> None:
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                coordinates: tuple[int, int] = (col * (config.WIDTH_PER_SQUARE), row * (config.HEIGHT_PER_SQUARE))
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
                if piece != enums.Piece.EMPTY and board.piecePickedUp != (row, col):
                    sprite = board.sprites[colour.value][piece.value]
                    if sprite is None:
                        print(f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
                    squareRect: pygame.Rect = pygame.Rect(
                        col * config.WIDTH_PER_SQUARE,
                        row * config.HEIGHT_PER_SQUARE,
                        config.WIDTH_PER_SQUARE,
                        config.HEIGHT_PER_SQUARE,
                    )
                    spriteRect = sprite.get_rect(center=squareRect.center)
                    _ = screen.blit(source=sprite, dest=spriteRect)
                elif board.piecePickedUp == (row, col):
                    mouseX, mouseY = pygame.mouse.get_pos()
                    if piece == enums.Piece.EMPTY:
                        continue
                    pickedUpSprite = board.sprites[colour.value][piece.value]
                    if pickedUpSprite is None:
                        print(f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
                    pieceBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
                    _ = pieceBackgroundSurface.fill(enums.RenderingColours.PIECE_PICKED_UP_BACKGROUND.value)
                    _ = screen.blit(source = pieceBackgroundSurface, dest = (col * config.WIDTH_PER_SQUARE, row * config.HEIGHT_PER_SQUARE))
                    moveBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
                    _ = moveBackgroundSurface.fill(enums.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value)
                    moves: list[tuple[int, int, enums.MoveType]] = moveHandling.getPseudoLegalMovesForPiece(board, row, col)
                    for move in moves:
                        moveRow, moveCol, _ = move
                        if moveRow == -1 and moveCol == -1: continue
                        _ = pygame.draw.circle(surface = screen, color = enums.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, center = (moveCol * config.WIDTH_PER_SQUARE + config.WIDTH_PER_SQUARE // 2, moveRow * config.HEIGHT_PER_SQUARE + config.HEIGHT_PER_SQUARE // 2), radius = config.WIDTH_PER_SQUARE // 8)
        if board.piecePickedUp != (-1, -1) and pickedUpSprite is not None:
            mouseX, mouseY = pygame.mouse.get_pos()
            spriteRect = pickedUpSprite.get_rect(center=(mouseX, mouseY))
            _ = screen.blit(source = pickedUpSprite, dest = spriteRect)

def main() -> None:
    environ["SDL_VSYNC"] = "1" # enable V-Sync
    _ = pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(size = (config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    print("Init: Pygame initialised")
    board: BoardHandling = BoardHandling()
    renderThreadInstance: Rendering = Rendering()
    fen.importFEN(board = board, fen = config.FEN_STARTING_POSITION)
    running: bool = True
    print("Init: Started!")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square: tuple[int, int] = board.getSquareUnderMousePosition() or (-1, -1)
                if square != (-1, -1):
                    if board.SideToMove == board.Board[square[0]][square[1]][1] and board.Board[square[0]][square[1]][0] != enums.Piece.EMPTY:
                        board.piecePickedUp = square    
            elif event.type == pygame.MOUSEBUTTONUP:
                board.processMove(fromSquare = board.piecePickedUp, toSquare = board.getSquareUnderMousePosition() or (-1, -1))
                board.piecePickedUp = (-1, -1)
        renderThreadInstance.drawBoardBackground(screen, board)
        #renderThreadInstance.debugRenderingMethod(board, screen)
        renderThreadInstance.renderBoard(screen, board)
        pygame.display.flip()
        _ = clock.tick(config.FPS)

    print("Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()