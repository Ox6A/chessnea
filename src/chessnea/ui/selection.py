"""Handles selection states for the UI."""

from dataclasses import dataclass

from chessnea.core import types


@dataclass
class Selection:
	state: types.SelectionState = types.SelectionState.NONE
	selectedSquare: types.Square | None = None
	possibleMoves: list[types.Move] | None = None
	mouseDown: bool = False
	deselectPieceOnMouseUp: bool = False

	def select(self, square: types.Square, possibleMoves: list[types.Move], state: types.SelectionState) -> None:
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
		self.state = types.SelectionState.NONE
		self.selectedSquare = None
		self.possibleMoves = None
		self.mouseDown = False
		self.deselectPieceOnMouseUp = False
		
