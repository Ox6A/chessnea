"""Handles the rendering of the chess board."""

import logging
import math
from dataclasses import dataclass

import pygame

from chessnea.core import types
from chessnea.rules import legal
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
		self.checkHighlightSurface: pygame.Surface = self.createCheckHighlightSurface()
		self.stationaryBoardCache: types.StationaryBoardCache | None = None
		self.highlightedBoardCache: types.HighlightedBoardCache | None = None
		self.moveAnimations: list[types.MoveAnimation] = []

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
	
	def getOtherPieceColour(self, colour: types.PieceColour) -> types.PieceColour:
		return types.PieceColour.BLACK if colour == types.PieceColour.WHITE else types.PieceColour.WHITE
 
	def getSquareRectAtGamePosition(self, square: types.Square) -> pygame.Rect:
		row, col = square
		size = self.layout.squarePx
		return pygame.Rect(
			col * size,
			self.layout.topBarPx + (row * size),
			size,
			size
		)

	def getBoardSquareAtSquare(self, square: types.Square, boardPosition: types.Position) -> types.BoardSquare:
		return types.BoardSquare((boardPosition.board[square[0]][square[1]][0], boardPosition.board[square[0]][square[1]][1]))

	def drawSelectedPiece(self, screen: pygame.Surface, sprite: pygame.Surface, mousePosition: tuple[int, int]) -> None:
		_ = screen.blit(source = sprite, dest = sprite.get_rect(center = mousePosition))
	
	def createCheckHighlightSurface(self) -> pygame.Surface:
		"""Creates a surface to highlight the king in check."""
		size: int = self.layout.squarePx
		surface: pygame.Surface = pygame.Surface((size, size), flags = pygame.SRCALPHA)
		centre: tuple[int, int] = (size // 2, size // 2)
		maxRadius: int = math.ceil(math.sqrt(2) * size / 2) # distance from centre to corner
		for radius in range(maxRadius, 0, -1):
			step: float = radius / maxRadius
			# colours to blend
			startColour: tuple[int, int, int, int]
			endColour: tuple[int, int, int, int]
			t: float
			if step <= 0.25:
				startColour, endColour = theme.SQUARE_HIGHLIGHT_CHECK_CENTRE, theme.SQUARE_HIGHLIGHT_CHECK_INNER
				t = step / 0.25
			elif step <= 0.89:
				startColour, endColour = theme.SQUARE_HIGHLIGHT_CHECK_INNER, theme.SQUARE_HIGHLIGHT_CHECK_OUTER
				t = (step - 0.25) / (0.89 - 0.25)
			else:
				continue

			colour: tuple[int, int, int, int] = (
				round(number = startColour[0] + (endColour[0] - startColour[0]) * t), # Red channel
				round(number = startColour[1] + (endColour[1] - startColour[1]) * t), # Green channel
				round(number = startColour[2] + (endColour[2] - startColour[2]) * t), # Blue channel
				round(number = startColour[3] + (endColour[3] - startColour[3]) * t) # Alpha channel
			)
			_ = pygame.draw.circle(surface = surface, color = colour, center = centre, radius = radius)
		return surface
 
	class BoardAnimations:
		@staticmethod
		def easeInOutCubic(t: float) -> float:
			"""Easing function for smooth animation."""
			if t < 0.5:
				return 4 * t ** 3
			else:
				return (t - 1) * (2 * t - 2) ** 2 + 1

		@staticmethod
		def startMoveAnimation(board: "BoardViewport", move: types.Move, boardPosition: types.Position) -> None:
			"""Starts a move animation for a given move.
			
			Args:
				board: The board viewport.
				move: The move to animate.
				boardPosition: The board position after the move.
			"""
			board.moveAnimations.append(types.MoveAnimation(
				fromSquare = move.fromSquare,
				toSquare = move.toSquare,
				piece = boardPosition.board[move.toSquare[0]][move.toSquare[1]][0],
				colour = boardPosition.board[move.toSquare[0]][move.toSquare[1]][1],
				startMs = pygame.time.get_ticks()
			))

	# Caching system: At (480px, static), 182.2 mus -> 74.7 mus. 2.44x speedup (1.86x at 960px)
	# Slower overall for per frame rendering: (480px), 185.1 mus -> 354.4 mus. 1.91x slowdown (2.47x slower at 960px)
	def refreshBoardCache(self, cacheLevel: types.CacheLevel, boardPosition: types.Position, selectionState: selection.Selection, hiddenSquares: frozenset[types.Square]) -> pygame.Surface:
		boardSurface: pygame.Surface = self.backgroundSurface.copy()
		rect: pygame.Rect
		sprite: pygame.Surface
		if cacheLevel == types.CacheLevel.STATIONARY:
			if legal.isKingInCheck(board = boardPosition.board, colour = boardPosition.sideToMove):
				kingSquare: types.Square | None = legal.findKing(board = boardPosition.board, colour = boardPosition.sideToMove)
				if kingSquare is not None:
					rect = self.getSquareRectAtGamePosition(square = kingSquare)
					rect = rect.move(0, -self.layout.topBarPx)
					_ = boardSurface.blit(source = self.checkHighlightSurface, dest = rect.topleft)
			for row, rank in enumerate[tuple[types.BoardSquare, ...]](boardPosition.board):
				for col, (piece, colour) in enumerate[types.BoardSquare](rank):
					if piece == types.Piece.EMPTY:
						continue
					sprite = self.getSprite(colour = colour, piece = piece)
					if types.Square((row, col)) in hiddenSquares:
						continue
					rect = self.getSquareRectAtGamePosition(square = (row, col))
					# Account for the top bar offset given by our helper
					rect = rect.move(0, -self.layout.topBarPx)
					_ = boardSurface.blit(source = sprite, dest = sprite.get_rect(center = rect.center))
		else: # types.CacheLevel.HIGHLIGHTED
			# Start with stationary cache
			if self.stationaryBoardCache is None:
				raise ValueError("Render: Stationary cache is None when refreshing highlighted cache")
			_ = boardSurface.blit(source = self.stationaryBoardCache.surface, dest = (0, 0))
   
			if selectionState.selectedSquare:
				rect = self.getSquareRectAtGamePosition(square = selectionState.selectedSquare)
				rect = rect.move(0, -self.layout.topBarPx)
				_ = boardSurface.blit(
					source = self.backgroundSurface,
					dest = rect.topleft,
					area = rect
				)
	
				selectedSquareHighlightSurface: pygame.Surface = pygame.Surface(
					size = rect.size,
					flags = pygame.SRCALPHA
				)
				_ = selectedSquareHighlightSurface.fill(color = theme.SQUARE_HIGHLIGHT)
				_ = boardSurface.blit(
					source = selectedSquareHighlightSurface,
					dest = rect.topleft
				)
				if not selectionState.mouseDown:
					row, col = selectionState.selectedSquare
					piece, colour = boardPosition.board[row][col]
					sprite = self.getSprite(colour = colour, piece = piece)
					_ = boardSurface.blit(source = sprite, dest = sprite.get_rect(center = rect.center))
	
			# Move highlighting
			if selectionState.possibleMoves:
				# We use a surface with alpha channel to draw the move highlighting dots, then blit it onto the board surface
				highlightSurface: pygame.Surface = pygame.Surface(size = boardSurface.get_size(), flags = pygame.SRCALPHA)
				for move in selectionState.possibleMoves:
					rect = self.getSquareRectAtGamePosition(square = move.toSquare)
					# Account for the top bar offset given by our helper
					rect = rect.move(0, -self.layout.topBarPx)
					# Empty square highlight
					if boardPosition.board[move.toSquare[0]][move.toSquare[1]][0] == types.Piece.EMPTY:
						_ = pygame.draw.aacircle(
							surface = highlightSurface, 
							color = theme.SQUARE_HIGHLIGHT_MOVE, 
							center = rect.center,
							radius = self.layout.squarePx // 8)
					else:
						# Set clip to bound circle to the square rect bounds
						previousClip: pygame.Rect = highlightSurface.get_clip()
						highlightSurface.set_clip(rect)
						_ = pygame.draw.aacircle(
							surface = highlightSurface,
							color = theme.SQUARE_HIGHLIGHT_MOVE_CAPTURE,
							center = rect.center,
							radius = self.layout.squarePx // 2 + self.layout.squarePx // 4,
							width = self.layout.squarePx // 4)
						highlightSurface.set_clip(previousClip)
				_ = boardSurface.blit(source = highlightSurface, dest = (0, 0))
		return boardSurface

	
	def renderBoard(self, screen: pygame.Surface, boardPosition: types.Position, selectionState: selection.Selection, mousePosition: tuple[int, int]) -> None:
		# We use 2 levels of cache in order to optimise rendering as much as possible.
		# Try stationary cache first
		cachedSurface: pygame.Surface
		boardState: types.Board = boardPosition.board
		timeNow: int = pygame.time.get_ticks()
		self.moveAnimations = [anim for anim in self.moveAnimations if timeNow - anim.startMs < anim.durationMs]
		squareBoundToCursor: types.Square | None = selectionState.selectedSquare if selectionState.mouseDown else None
		hiddenSquares: frozenset[types.Square] = frozenset(anim.toSquare for anim in self.moveAnimations)
		if squareBoundToCursor is not None:
			hiddenSquares = hiddenSquares | {squareBoundToCursor}
		if self.stationaryBoardCache is None or self.stationaryBoardCache.boardState != boardState or self.stationaryBoardCache.hiddenSquares != hiddenSquares:
			# Stationary cache miss
			cachedSurface = self.refreshBoardCache(cacheLevel = types.CacheLevel.STATIONARY, boardPosition = boardPosition, selectionState = selectionState, hiddenSquares = hiddenSquares)
			self.stationaryBoardCache = types.StationaryBoardCache(
				surface = cachedSurface,
				hiddenSquares = hiddenSquares,
				boardState = boardState
			)
			# Invalidate highlighted cache when stationary cache is rebuilt
			self.highlightedBoardCache = None

		# Try highlighted cache next
		if self.highlightedBoardCache is None or self.highlightedBoardCache.selectedSquare != selectionState.selectedSquare:
			# Highlighted cache miss
			cachedSurface = self.refreshBoardCache(cacheLevel = types.CacheLevel.HIGHLIGHTED, boardPosition = boardPosition, selectionState = selectionState, hiddenSquares = hiddenSquares)
			self.highlightedBoardCache = types.HighlightedBoardCache(
				surface = cachedSurface,
				selectedSquare = selectionState.selectedSquare,
				possibleMoves = selectionState.possibleMoves
			)
		_ = screen.blit(source = self.highlightedBoardCache.surface, dest = (0, self.layout.topBarPx))

		# Render move animations
		for anim in self.moveAnimations:
			t: float = self.BoardAnimations.easeInOutCubic(t = (timeNow - anim.startMs) / anim.durationMs)
			start: pygame.Vector2 = pygame.Vector2(self.getSquareRectAtGamePosition(square = anim.fromSquare).center)
			end: pygame.Vector2 = pygame.Vector2(self.getSquareRectAtGamePosition(square = anim.toSquare).center)
			sprite = self.getSprite(colour = anim.colour, piece = anim.piece)
			_ = screen.blit(source = sprite, dest = sprite.get_rect(center = start.lerp(end, t)))

		# Render selected piece if dragging
		if squareBoundToCursor is not None:
			piece, colour = boardState[squareBoundToCursor[0]][squareBoundToCursor[1]]
			sprite: pygame.Surface = self.getSprite(colour = colour, piece = piece)
			self.drawSelectedPiece(screen = screen, sprite = sprite, mousePosition = mousePosition)