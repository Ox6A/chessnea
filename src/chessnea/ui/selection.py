"""Handles selection states for the UI."""

from dataclasses import dataclass

from chessnea.core.types import Move, Square


@dataclass
class SelectionState:
	selectedSquare: Square | None = None
	possibleMoves: tuple[Move, ...] = ()
	dragging: bool = False 

	def select(self, square: Square, possibleMoves: tuple[Move, ...], dragging: bool) -> None:
		"""Updates the selection state with the given square, possible moves, and dragging status."""
		self.selectedSquare = square
		self.possibleMoves = possibleMoves
		self.dragging = dragging
	
	def clear(self) -> None:
		"""Clears the selection state."""
		self.selectedSquare = None
		self.possibleMoves = ()
		self.dragging = False
		