from datetime import datetime_CAPI
import logging
import math
from dataclasses import dataclass

import pygame

from chessnea.core import types
from chessnea.ui import assets, selection, theme

logger: logging.Logger = logging.getLogger(name = __name__)

MIN_BOARD_PX: int = 480
TOP_BAR_PX_FACTOR: float = 0 # Standard factor is 1/16
BOARD_TO_RESOLUTION_FACTOR: float = 0.8 # 80% of screen width/height is used

@dataclass(frozen = True)
class Layout:
	boardPx: int
	squarePx: int
	topBarPx: int
	window: tuple[int, int]

	@classmethod
	def fromBoardPx(cls, boardPx: int) -> "Layout":
		boardPx = max(MIN_BOARD_PX, boardPx) # Enforce minimum board size
		boardPx -= boardPx % 8 # Remove excess pixels after setting the 8 square division factor
		topBar = math.floor(boardPx * TOP_BAR_PX_FACTOR)
		return cls(
			boardPx = boardPx,
			squarePx = boardPx // 8,
			topBarPx = topBar,
			# topBarPx = boardPx // 16,
			window = (boardPx, boardPx + topBar),
		)

class BoardViewport:
	def __init__(self, layout: Layout) -> None:
		self.layout: Layout = layout
		self.sprites: dict[tuple[types.PieceColour, types.Piece], pygame.Surface] = assets.loadSprites(squarePx = self.layout.squarePx)
		self.backgroundSurface: pygame.Surface = self.createBoardBackgroundSurface()
		self.stationaryBoardCache: types.StationaryBoardCache | None = None
		self.highlightedBoardCache: types.HighlightedBoardCache | None = None

	def createBoardBackgroundSurface(self) -> pygame.Surface:
		surface: pygame.Surface = pygame.Surface((self.layout.boardPx, self.layout.boardPx))
		for row in range(8):
			for col in range(8):
				colour : tuple[int, int, int]
				if (row + col) % 2 == 0:
					colour = theme.SQUARE_WHITE
				else:
					colour = theme.SQUARE_BLACK
				_ = pygame.draw.rect(surface = surface, color = colour, rect = (col * self.layout.squarePx, row * self.layout.squarePx, self.layout.squarePx, self.layout.squarePx))
		return surface

	# def drawBoardBackgroundSurface(self, screen: pygame.Surface) -> None:
	# 	_ = screen.blit(source = self.backgroundSurface, dest = (0, self.layout.topBarPx))

	def getSprite(self, colour: types.PieceColour, piece: types.Piece) -> pygame.Surface:
		try:
			return self.sprites[(colour, piece)]
		except KeyError as e:
			logger.error(msg = f"Render: Sprite for {colour.name} {piece.name} not found in loaded sprites")
			raise ValueError(f"Render: Sprite for {colour.name} {piece.name} not found in loaded sprites") from e
	
	def getSquareAt(self, mousePosition: tuple[int, int]) -> types.Square | None:
		mouseX, mouseY = mousePosition
		mouseY -= self.layout.topBarPx
		row: int = mouseY // self.layout.squarePx
		col: int = mouseX // self.layout.squarePx
		if 0 <= row < 8 and 0 <= col < 8:
			return (row, col)
		return None
	
	def getSquareRectAtGamePosition(self, square: types.Square) -> pygame.Rect:
		row, col = square
		size = self.layout.squarePx
		return pygame.Rect(
			col * size,
			self.layout.topBarPx + (row * size),
			size,
			size
		)

	def drawSelectedPiece(self, screen: pygame.Surface, sprite: pygame.Surface, mousePosition: tuple[int, int]) -> None:
		_ = screen.blit(source = sprite, dest = sprite.get_rect(center = mousePosition))

	# def refreshBoardCache(self, screen: pygame.Surface, boardPosition: types.Position, selectionState: selection.Selection, mousePosition: tuple[int, int]) -> None:
	# 	self.drawBoardBackgroundSurface(screen = screen)
	# 	selectedPiecesToRender: list[pygame.Surface] = []
	# 	for row, rank in enumerate[tuple[types.BoardSquare, ...]](boardPosition.board):
	# 		for col, (piece, colour) in enumerate[types.BoardSquare](rank):
	# 			if piece == types.Piece.EMPTY:
	# 				continue
	# 			sprite: pygame.Surface = self.getSprite(colour = colour, piece = piece)
	# 			if selectionState.selectedSquare == types.Square((row, col)) and selectionState.mouseDown == True:
	# 				selectedPiecesToRender.append(sprite)
	# 				continue
	# 			rect: pygame.Rect = self.getSquareRectAtGamePosition(square = (row, col))
	# 			_ = screen.blit(source = sprite, dest = sprite.get_rect(center = rect.center))
	
	# 	# Render selected pieces
	# 	for sprite in selectedPiecesToRender:
	# 		self.drawSelectedPiece(screen = screen, sprite = sprite, mousePosition = mousePosition)

	def refreshBoardCache(self, cacheLevel: types.CacheLevel, boardPosition: types.Position, selectionState: selection.Selection) -> pygame.Surface:
		boardSurface: pygame.Surface = self.backgroundSurface.copy()
		if cacheLevel == types.CacheLevel.STATIONARY:
			for row, rank in enumerate[tuple[types.BoardSquare, ...]](boardPosition.board):
				for col, (piece, colour) in enumerate[types.BoardSquare](rank):
					if piece == types.Piece.EMPTY:
						continue
					sprite: pygame.Surface = self.getSprite(colour = colour, piece = piece)
					if selectionState.selectedSquare == types.Square((row, col)) and selectionState.mouseDown == True:
						continue
					rect: pygame.Rect = self.getSquareRectAtGamePosition(square = (row, col))
					# Account for the top bar offset given by our helper
					rect = rect.move(0, -self.layout.topBarPx)
					_ = boardSurface.blit(source = sprite, dest = sprite.get_rect(center = rect.center))
		else: # types.CacheLevel.HIGHLIGHTED
			# Start with stationary cache
			if self.stationaryBoardCache is None:
				raise ValueError("Render: Stationary cache is None when refreshing highlighted cache")
			_ = boardSurface.blit(source = self.stationaryBoardCache.surface, dest = (0, 0))
			# Rest is to-do
		return boardSurface

	
	def renderBoard(self, screen: pygame.Surface, boardPosition: types.Position, selectionState: selection.Selection, mousePosition: tuple[int, int]) -> None:
		boardState: types.Board = boardPosition.board
		cachedSurface: pygame.Surface
		
		# We use 2 levels of cache in order to optimise rendering as much as possible.
		# Try stationary cache first
		squareBoundToCursor: types.Square | None = selectionState.selectedSquare if selectionState.mouseDown else None
		if self.stationaryBoardCache is None or self.stationaryBoardCache.boardState != boardState or self.stationaryBoardCache.selectedSquare != squareBoundToCursor:
			# Stationary cache miss
			logger.debug(msg = "Render: Stationary cache miss")
			cachedSurface = self.refreshBoardCache(cacheLevel = types.CacheLevel.STATIONARY, boardPosition = boardPosition, selectionState = selectionState)
			self.stationaryBoardCache = types.StationaryBoardCache(
				surface = cachedSurface,
				selectedSquare = squareBoundToCursor,
				boardState = boardState
			)
			# Invalidate highlighted cache when stationary cache is rebuilt
			self.highlightedBoardCache = None

		# Try highlighted cache next
		if self.highlightedBoardCache is None or self.highlightedBoardCache.selectedSquare != selectionState.selectedSquare:
			# Highlighted cache miss
			logger.debug(msg = "Render: Highlighted cache miss")
			cachedSurface = self.refreshBoardCache(cacheLevel = types.CacheLevel.HIGHLIGHTED, boardPosition = boardPosition, selectionState = selectionState)
			self.highlightedBoardCache = types.HighlightedBoardCache(
				surface = cachedSurface,
				selectedSquare = selectionState.selectedSquare,
				possibleMoves = selectionState.possibleMoves
			)
		_ = screen.blit(source = self.highlightedBoardCache.surface, dest = (0, self.layout.topBarPx))

		# Render selected piece if dragging
		if squareBoundToCursor is not None:
			piece, colour = boardState[squareBoundToCursor[0]][squareBoundToCursor[1]]
			sprite: pygame.Surface = self.getSprite(colour = colour, piece = piece)
			self.drawSelectedPiece(screen = screen, sprite = sprite, mousePosition = mousePosition)