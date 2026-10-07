"""Handles selection states for the UI."""

from dataclasses import dataclass

from chessnea.core.types import Move, SelectionState, Square


@dataclass
class Selection:
	state: SelectionState = SelectionState.NONE
	selectedSquare: Square | None = None
	possibleMoves: tuple[Move, ...] = ()
	mouseDown: bool = False
	deselectPieceOnMouseUp: bool = False

	def select(self, square: Square, possibleMoves: tuple[Move, ...], state: SelectionState) -> None:
		"""Updates the selection state with the given square, possible moves, and dragging status.

		Args:
			square: Selected board square as types.Square.
			possibleMoves: Possible moves associated with the selected piece.
			state: Selection state.
		"""
		self.selectedSquare = square
		self.state = state
		self.possibleMoves = possibleMoves
		self.mouseDown = True
		self.deselectPieceOnMouseUp = False
	
	def clear(self) -> None:
		"""Clears the selection state."""
		self.state = SelectionState.NONE
		self.selectedSquare = None
		self.possibleMoves = ()
		self.mouseDown = False
		self.deselectPieceOnMouseUp = False
		
