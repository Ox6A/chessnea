"""Draws the top bar of the chess game"""

from dataclasses import dataclass

import pygame

from chessnea.core import clock, types
from chessnea.ui import board, theme


@dataclass(frozen = True)
class Button:
	"""A class representing a button in the top bar of the chess game.
	
	Attributes:
		rect: The rectangle representing the button's position and size.
		label: The text label of the button.
		textSurface: The surface containing the rendered text of the button.
		alignRight: A boolean indicating whether the button is aligned to the right side of the bar.
	"""

	rect: pygame.Rect
	label: str
	textSurface: pygame.Surface
	alignRight: bool

class Bar:
	"""A class representing the top bar of the chess game."""

	def __init__(self, layout: board.Layout, padLeftLabels: list[str], padRightLabels: list[str]) -> None:
		"""Initializes the Bar class.

		Args:
			layout: The layout of the bar.
			padLeftLabels: The labels to be displayed on the left side of the bar.
			padRightLabels: The labels to be displayed on the right side of the bar.
		"""
		textSurface: pygame.Surface
		width: int

		self.rect: pygame.Rect = pygame.Rect(0, 0, layout.window[0], layout.topBarPx)
		self.paddingX: int = layout.topBarPx // 3
		self.dividerWidth: int = max(1, layout.topBarPx // 25)
		self.bottomLineThickness: int = max(2, layout.topBarPx // 16)

		fontSize: int = layout.topBarPx // 2
		self.fontRegular: pygame.font.Font = pygame.font.Font(filename = theme.FONT_REGULAR, size = fontSize)
		self.fontMedium: pygame.font.Font = pygame.font.Font(filename = theme.FONT_MEDIUM, size = fontSize)
		self.fontBold: pygame.font.Font = pygame.font.Font(filename = theme.FONT_BOLD, size = fontSize)

		self.buttons: list[Button] = []
		leftX: int = 0
		for label in padLeftLabels:
			textSurface= self.fontMedium.render(text = label, antialias = True, color = theme.TEXT_PRIMARY_COLOUR)
			width = textSurface.get_width() + (self.paddingX * 2)
			self.buttons.append(Button(
				rect = pygame.Rect(leftX, 0, width, self.rect.height),
				label = label,
				textSurface = textSurface,
				alignRight = False
			))
			leftX += width + self.dividerWidth
		rightX: int = self.rect.width
		for label in padRightLabels:
			textSurface = self.fontMedium.render(text = label, antialias = True, color = theme.TEXT_PRIMARY_COLOUR)
			width = textSurface.get_width() + (self.paddingX * 2)
			rightX -= width
			self.buttons.append(Button(
				rect = pygame.Rect(rightX, 0, width, self.rect.height),
				label = label,
				textSurface = textSurface,
				alignRight = True
			))
			rightX -= self.dividerWidth
	
	def getButtonAtPos(self, mousePosition: tuple[int, int]) -> Button | None:
		"""Returns the button at the given position, if any.

		Args:
			pos: The position to check for a button.
		Returns:
			The button at the given position, or None if there is no button at that position.
		"""
		for button in self.buttons:
			if button.rect.collidepoint(mousePosition):
				return button
		return None

	def draw(self, screen: pygame.Surface, mousePosition: tuple[int, int], clock: clock.Clock, sideToMove: types.PieceColour, clockEnabled: bool) -> None:
		_ = pygame.draw.rect(surface = screen, color = theme.BAR_COLOUR, rect = self.rect)
		isLeftMouseButtonHeld: bool = pygame.mouse.get_pressed()[0]
		for button in self.buttons:
			if button.rect.collidepoint(mousePosition):
				hoverColour: tuple[int, int, int] = theme.BAR_BUTTON_PRESSED_COLOUR if isLeftMouseButtonHeld else theme.BAR_BUTTON_HOVER_COLOUR
				_ = pygame.draw.rect(surface = screen, color = hoverColour, rect = button.rect)
			_ = screen.blit(source = button.textSurface, dest = button.textSurface.get_rect(center = button.rect.center))
			# We need to ensure to draw the divider on the side of the button that is facing the centre of the bar.
			dividerX: int = button.rect.left - self.dividerWidth if button.alignRight else button.rect.right
			_ = pygame.draw.rect(surface = screen, color = theme.BAR_OUTLINE_COLOUR, rect = pygame.Rect(dividerX, 0, self.dividerWidth, self.rect.height))
		_ = pygame.draw.rect(surface = screen, color = theme.BAR_OUTLINE_COLOUR, rect = pygame.Rect(0, self.rect.height - self.bottomLineThickness, self.rect.width, self.bottomLineThickness))
		self.drawClock(screen = screen, clock = clock, sideToMove = sideToMove, clockEnabled = clockEnabled)
		

	def drawClock(self, screen: pygame.Surface, clock: clock.Clock, sideToMove: types.PieceColour, clockEnabled: bool) -> None:
		"""Draws the clock on the bar.

		Args:
			screen: The surface to draw on.
			clock: The clock to draw.
			sideToMove: The side that is to move.
			clockEnabled: Whether the clock is enabled or not.
		"""
		segments: list[pygame.Surface] = []
		for colour in (types.PieceColour.WHITE, types.PieceColour.BLACK):
			active: bool = colour == sideToMove
			font: pygame.font.Font = self.fontBold if active else self.fontMedium
			textColour: tuple[int, int, int] = theme.TEXT_PRIMARY_COLOUR if active else theme.TEXT_SECONDARY_COLOUR
			if not clockEnabled:
				textColour = theme.TEXT_DISABLED_COLOUR
			segments.append(font.render(text = clock.getTimeAsString(sideToMove = colour), antialias = True, color = textColour))
			# Add the divider between the two segments, but only if we're on the white segment.
			if colour == types.PieceColour.WHITE:
				segments.append(self.fontRegular.render(text = " | ", antialias = True, color = theme.TEXT_PRIMARY_COLOUR))
		segments.append(self.fontRegular.render(text = f" · {sideToMove.name.capitalize()}'s turn", antialias = True, color = theme.TEXT_PRIMARY_COLOUR))

		totalWidth: int = sum(segment.get_width() for segment in segments)
		x: int = (self.rect.width - totalWidth) // 2
		for segment in segments:
			_ = screen.blit(source = segment, dest = segment.get_rect(midleft = (x, self.rect.centery)))
			x += segment.get_width()