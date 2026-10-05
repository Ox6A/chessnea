import logging

import pygame

from chessnea.core import types
from chessnea.ui import theme

logger: logging.Logger = logging.getLogger(__name__)

PIECE_TYPE: dict[types.Piece, str] = {
	types.Piece.PAWN: "P",
	types.Piece.KNIGHT: "N",
	types.Piece.BISHOP: "B",
	types.Piece.ROOK: "R",
	types.Piece.QUEEN: "Q",
	types.Piece.KING: "K",
}

PIECE_COLOUR: dict[types.PieceColour, str] = {
	types.PieceColour.WHITE: "w",
	types.PieceColour.BLACK: "b",
}

# Changed output format from a integer indexed array of surfaces to a dictionary with keys as (colour, piece) tuples
def loadSprites(squarePx: int) -> dict[tuple[types.PieceColour, types.Piece], pygame.Surface]:
	sprites: dict[tuple[types.PieceColour, types.Piece], pygame.Surface] = {}
	size: int = int(squarePx * 0.9) # scale down to 90% of square size
	for colour in types.PieceColour:
		if colour == types.PieceColour.EMPTY:
			continue
		for piece in types.Piece:
			if piece == types.Piece.EMPTY:
				continue
			# Convert piece type and colour to filename on disk
			filename: str = PIECE_COLOUR[colour] + PIECE_TYPE[piece] + ".svg"
			filePath: str = str(theme.ASSETS_PIECE_SET_DIR) + "/" + filename
			try:
				# Load the .svg as a scaled pygame.Surface to the square size for sprite quality
				img: pygame.Surface = pygame.image.load_sized_svg(file = filePath, size = (size, size)).convert_alpha()
				logger.debug(msg = f"UI/Assets: Loaded piece {types.PieceToDisplayName.COLOUR[colour]} {types.PieceToDisplayName.PIECE[piece]} from {filePath}")
			except FileNotFoundError:
				logger.error(msg = f"UI/Assets: Could not find piece sprite file {filename} in {theme.ASSETS_PIECE_SET_DIR}!")
				raise FileNotFoundError(f"UI/Assets: Could not find piece sprite file {filename} in {theme.ASSETS_PIECE_SET_DIR}!")
			sprites[(colour, piece)] = img
	return sprites