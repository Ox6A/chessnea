"""Draws panels and overlays on top of the chess board."""

import pygame

from chessnea.core import types
from chessnea.ui import board, theme


class GameOverOverlay:
	"""Represents the overlay displayed when the game is over."""
	def __init__(self, layout: board.Layout, reason: types.GameOverReason, winner: types.PieceColour | None = None, icon: pygame.Surface | None = None) -> None:
		self.surface: pygame.Surface = pygame.Surface(size = layout.window, flags = pygame.SRCALPHA)
		_ = self.surface.fill(color = theme.OVERLAY_DIM)
		title: str
		subtitle: str
		winnerName: str = winner.name.capitalize() if winner is not None else ""
		if reason == types.GameOverReason.CHECKMATE:
			title = "Checkmate"
			subtitle = f"{winnerName} wins!"
		elif reason == types.GameOverReason.STALEMATE:
			title = "Stalemate"
			subtitle = "Draw!"
		elif reason == types.GameOverReason.INSUFFICIENT_MATERIAL:
			title = "Draw"
			subtitle = "Insufficient material!"
		elif reason == types.GameOverReason.FIFTY_MOVE_RULE:
			title = "Draw"
			subtitle = "Fifty-move rule!"
		elif reason == types.GameOverReason.THREEFOLD_REPETITION:
			title = "Draw"
			subtitle = "Threefold repetition!"

		panelRect: pygame.Rect = pygame.Rect(0, 0, layout.boardPx // 2, layout.boardPx // 3)
		panelRect.center = (layout.window[0] // 2, layout.window[1] // 2)
		
		# shadow
		radius: int = layout.squarePx // 6
		shadowRect: pygame.Rect = panelRect.move(0, layout.squarePx // 12)
		_ = pygame.draw.rect(surface = self.surface, rect = shadowRect, color = theme.PANEL_SHADOW_COLOUR, border_radius = radius)

		_ = pygame.draw.rect(surface = self.surface, rect = panelRect, color = theme.PANEL_COLOUR, border_radius = layout.squarePx // 6)

  
		titleFont: pygame.font.Font = pygame.font.Font(filename = theme.FONT_BOLD, size = layout.squarePx // 2)
		bodyFont: pygame.font.Font = pygame.font.Font(filename= theme.FONT_REGULAR, size = layout.squarePx // 4)
		titleSurface: pygame.Surface = titleFont.render(text = title, antialias = True, color = theme.TEXT_PRIMARY_COLOUR)
		titleCentreY: int = panelRect.top + panelRect.height // 4
		titleRect: pygame.Rect = titleSurface.get_rect(center = (panelRect.centerx, titleCentreY))

		if icon is not None:
			iconSize: int = layout.squarePx // 2
			gap: int = layout.squarePx // 8
			scaledIcon: pygame.Surface = pygame.transform.smoothscale(surface = icon, size = (iconSize, iconSize))
			groupWidth: int = iconSize + gap + titleRect.width
			iconRect: pygame.Rect = scaledIcon.get_rect(midleft = (panelRect.centerx - groupWidth // 2, titleCentreY))
			titleRect.midleft = (iconRect.right + gap, titleCentreY)
			_ = self.surface.blit(source = scaledIcon, dest = iconRect)

		_ = self.surface.blit(source = titleSurface, dest = titleRect)
		subtitleSurface: pygame.Surface = bodyFont.render(text = subtitle, antialias = True, color = theme.TEXT_SECONDARY_COLOUR)
		_ = self.surface.blit(source = subtitleSurface, dest = subtitleSurface.get_rect(center = (panelRect.centerx, panelRect.top + panelRect.height // 2)))
  
		self.newGameButtonRect: pygame.Rect = pygame.Rect(0, 0, layout.boardPx // 4, layout.squarePx // 2)
		self.newGameButtonRect.midbottom = (panelRect.centerx, panelRect.bottom - layout.squarePx // 4)
		self.buttonRadius: int = layout.squarePx // 10
		_ = pygame.draw.rect(surface = self.surface, color = theme.PANEL_BUTTON_COLOUR, rect = self.newGameButtonRect, border_radius = self.buttonRadius)
		self.buttonText: pygame.Surface = bodyFont.render(text = "New Game", antialias = True, color = theme.TEXT_PRIMARY_COLOUR)
		_ = self.surface.blit(source = self.buttonText, dest = self.buttonText.get_rect(center = self.newGameButtonRect.center))

	def draw(self, screen: pygame.Surface, mousePosition: tuple[int, int]) -> None:
		"""Draws the overlay on the given screen."""
		_ = screen.blit(source = self.surface, dest = (0, 0))
		hovered: bool = self.newGameButtonRect.collidepoint(mousePosition)
		colour: tuple[int, int, int] = theme.PANEL_BUTTON_HOVER_COLOUR if hovered else theme.PANEL_BUTTON_COLOUR
		_ = pygame.draw.rect(surface = screen, color = colour, rect = self.newGameButtonRect, border_radius = self.buttonRadius)
		_ = screen.blit(source = self.buttonText, dest = self.buttonText.get_rect(center = self.newGameButtonRect.center))
		_ = pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hovered else pygame.SYSTEM_CURSOR_ARROW)