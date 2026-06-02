import pygame

import chessnea.config as config
import chessnea.enums as enums

def loadSprites() -> list[list[pygame.Surface | None]]:
    # Loads all the sprites needed for game board rendering from disk in .svg format for scaling
    sprites: list[list[pygame.Surface | None]] = [[None for _ in range(6)] for _ in range(2)] # Empty nested list for sprites of all chess pieces in all colours
    for colour in enums.PieceColour:
        for piece in enums.Piece:
            if piece != enums.Piece.EMPTY:
                filename: str = f"{colour.name.lower()[0]}{piece.name.upper()[0]}.svg" # Expected file name format
                if piece.name.lower() == "knight":
                    filename = f"{colour.name.lower()[0]}N.svg"
                try:
                    img: pygame.Surface = pygame.image.load_sized_svg(file = f"{config.ASSETS_PIECES_DIRECTORY}/{config.PIECE_SET}/{filename}", size = (config.WIDTH_PER_SQUARE * 0.9, config.HEIGHT_PER_SQUARE * 0.9)).convert_alpha() # Scaling and loading from disk
                except (FileNotFoundError, pygame.error) as e: # Handle missing sprites
                    print(f"ERROR at Init: Failed to load sprite for {colour.name} {piece.name} from {filename}: {e}")
                else:
                    print(f"Init: Loaded sprite for {colour.name} {piece.name} from {filename}")
                    sprites[colour.value][piece.value] = img
    for colour in enums.PieceColour:
        for piece in enums.Piece:
            if piece != enums.Piece.EMPTY and sprites[colour.value][piece.value] is None: # Double check if sprites were loaded correctly
                print(f"ERROR at Init: Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
                raise ValueError(f"Failed to load sprite (Sprite for {colour.name} {piece.name} is None)")
    return sprites