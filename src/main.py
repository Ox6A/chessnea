import pygame
# pyright: reportUnusedVariable=false

# Globals
DEFAULT_WIDTH, DEFAULT_HEIGHT = 600, 600
FPS = 60

# Colours
SQUARE_WHITE = (240, 217, 181)
SQUARE_BLACK = (181, 136, 99)

class Board:
    def __init__(self): 
        self.board = []
        for i in range(8):  
            row = []
            for i1 in range(8):
                row.append(0)  # Placeholder for pieces
            self.board.append(row)
    
    def drawBoard(self, screen) -> None:
        cellWidth = 0
        width, height = screen.get_size()
        if width > height:
            cellWidth = height // 8
        else:
            cellWidth = width // 8

        screen.fill((240, 217, 181))  # Background
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    color = SQUARE_WHITE
                else:
                    color = SQUARE_BLACK
                pygame.draw.rect(screen, color, rect=(col * cellWidth, row * cellWidth, cellWidth, cellWidth))
        

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
