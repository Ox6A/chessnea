from chessnea.core.types import Move, Square


class SelectionState:
	selectedSquare: Square | None = None
	possibleMoves: tuple[Move, ...] = ()
	dragging: bool = False 

	def select(self, square: Square, possibleMoves: tuple[Move], dragging: bool) -> None:
		self.selectedSquare = square
		self.possibleMoves = possibleMoves
		self.dragging = dragging
	
	def clear(self) -> None:
		self.selectedSquare = None
		self.possibleMoves = ()
		self.dragging = False
		