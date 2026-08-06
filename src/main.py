#!/usr/bin/python
import logging
import typing
from os import environ

import pygame

import chessnea.board as boardHandling
import chessnea.clock as clockHandling
from chessnea import config, render, ui

logger: logging.Logger = logging.getLogger(name = __name__)

def main() -> None:
	logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
	logger.info(msg = "Init: Chessnea version " + config.VERSION)
	logger.info(msg = "Init: Running initialisation...")
	environ["SDL_VSYNC"] = "1" # enable V-Sync
	_ = pygame.init()
	logger.info(msg = "Init: Pygame initialised!")
	screen: pygame.Surface = pygame.display.set_mode(size = (config.WindowDefaults.WINDOW_WIDTH.value, config.WindowDefaults.WINDOW_HEIGHT.value))
	logger.info(msg = f"Init: Display created with configuration: {config.WindowDefaults.WINDOW_WIDTH.value}x{config.WindowDefaults.WINDOW_HEIGHT.value} at {config.WindowDefaults.FPS.value} FPS")
	pygame.display.set_caption("Chess")
	clock: pygame.time.Clock = pygame.time.Clock()
	board: boardHandling.BoardHandling = boardHandling.BoardHandling()
	_ = board.loadSpritesForBoard()
	renderThreadInstance: render.Rendering = render.Rendering()
	logger.info(msg = "Init: Starting main UI...")
	menuBarInstance: ui.MenuBar = ui.MenuBar()
	gameBarInstance: ui.MenuBar = ui.MenuBar()
	ui.addStandardUIItems(menuBarInstance = menuBarInstance, gameBarInstance = gameBarInstance)
	ui.loadBoardInUI(board = board)
	ui.loadMenuBar(menuBar = menuBarInstance)
	ui.loadGameBar(gameBar = gameBarInstance)
	clockInstance = ui.loadClock(clock = clockHandling.Clock())
	logger.info(msg = "Init: Started UI initialisation")
	_ = board.resetBoard()
	running: bool = True
	promotionUIRects: list[tuple[pygame.Rect, config.Piece]] = []
	gameOverButtonRects: list[tuple[pygame.Rect, str]] = []
	logger.info(msg = "Init: Initialisation finished")
	logger.info(msg = "Init: Started main game loop")
	currentCursor:int = pygame.SYSTEM_CURSOR_ARROW
	while running:
		mouseX, mouseY = pygame.mouse.get_pos()
		menuBarHoveringOverButton: config.MenuItem | None = menuBarInstance.checkIfHoveringOverMenuItem(mouseX = mouseX, mouseY = mouseY)
		gameBarHoveringOverButton: config.MenuItem | None = gameBarInstance.checkIfHoveringOverMenuItem(mouseX = mouseX, mouseY = mouseY)
		hoveringOverButton: config.MenuItem | None = menuBarHoveringOverButton or gameBarHoveringOverButton
		for event in pygame.event.get():
			targetSquare: tuple[int, int] | tuple[typing.Literal[-1], typing.Literal[-1]]
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				eventKey: int = typing.cast(int, event.key)
				if eventKey == pygame.key.key_code(name = "P") and board.hasFirstMoveHappened:
					for button in menuBarInstance.menuItems:
						if button.itemType == config.ItemType.DROPDOWN and button.children:
							for child in button.children:
								if child.name == "Pause Game":
									child.toggled = not child.toggled
									break
					_ = ui.ConnectorFunctions.toggleClock()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if hoveringOverButton:
					continue
				if not board.gameState.gameOver:
					if board.hasFirstMoveHappened and not clockInstance.clockRunning:
						continue
					if board.pendingPromotion:
						mouseX, mouseY = pygame.mouse.get_pos()
						for uiRect, piece in promotionUIRects:
							if uiRect.collidepoint(mouseX, mouseY):
								boardHandling.completePromotion(board = board, promotionPieceType = piece)
								board.syncBoardFlipStateToSideToMove()
								promotionUIRects = []
								logger.debug(msg = f"Main: Processed promotion to {piece.name}")
								break
						continue
					targetSquare = board.getSquareUnderMousePosition() or (-1, -1)
					if targetSquare != (-1, -1):
						piece, colour = board.Board[targetSquare[0]][targetSquare[1]][0], board.Board[targetSquare[0]][targetSquare[1]][1]
						if board.SideToMove == colour and piece != config.Piece.EMPTY:
							board.piecePickedUp = targetSquare   
							row, col = targetSquare
							board.piecePickedUpLegalMoves = boardHandling.getLegalMovesForPiece(board = board, row = row, col = col)
							board.selectedSquare = (-1, -1)
							board.selectedSquareLegalMoves = []
							logger.debug(msg = f"Main: Picked up piece at square {targetSquare} of type {board.Board[targetSquare[0]][targetSquare[1]][0]} and colour {board.Board[targetSquare[0]][targetSquare[1]][1]}")
			elif event.type == pygame.MOUSEBUTTONUP:
				if board.gameState.gameOver:
					for buttonRect, callback in gameOverButtonRects:
						if buttonRect.collidepoint(mouseX, mouseY):
							if callback == "newGame":
								_ = ui.ConnectorFunctions.newGame()
								logger.info(msg = "Main: Reset board after game over")
							break
				returnType: config.ReturnType
				if hoveringOverButton:
					if not menuBarInstance.hidden:
						if hoveringOverButton.children and menuBarInstance.openItem == hoveringOverButton:
							menuBarInstance.openItem = None
						elif hoveringOverButton.children:
							menuBarInstance.openItem = hoveringOverButton
						else:
							if hoveringOverButton.itemType == config.ItemType.TOGGLE:
								if hoveringOverButton.name == "Pause Game" and not board.hasFirstMoveHappened:
									logger.warning(msg = "Main: Cannot pause as no moves have been made yet!")
									continue
								hoveringOverButton.toggled = not hoveringOverButton.toggled
								_ = menuBarInstance.runConnectorFunction(item = hoveringOverButton)
							else:
								returnType = menuBarInstance.runConnectorFunction(item = hoveringOverButton)
								if returnType == config.ReturnType.QUIT_GAME:
									running = False
								menuBarInstance.openItem = None
						continue
					else:
						if hoveringOverButton.children and gameBarInstance.openItem == hoveringOverButton:
							gameBarInstance.openItem = None
						elif hoveringOverButton.children:
							gameBarInstance.openItem = hoveringOverButton
						else:
							if hoveringOverButton.itemType == config.ItemType.TOGGLE:
								hoveringOverButton.toggled = not hoveringOverButton.toggled
								_ = gameBarInstance.runConnectorFunction(item = hoveringOverButton)
							else:
								returnType = gameBarInstance.runConnectorFunction(item = hoveringOverButton)
								if returnType == config.ReturnType.QUIT_GAME:
									running = False
								gameBarInstance.openItem = None
						continue
				if not board.gameState.gameOver:
					if board.pendingPromotion:
						continue
					if board.hasFirstMoveHappened and not clockInstance.clockRunning:
						board.piecePickedUp = (-1, -1)
						board.piecePickedUpLegalMoves = []
						board.selectedSquare = (-1, -1)
						board.selectedSquareLegalMoves = []
						continue
					targetSquare = board.getSquareUnderMousePosition() or (-1, -1)
					valid: bool = False
					if board.piecePickedUp != (-1, -1):
						fromSquare = board.piecePickedUp
						fromLegalMoves: list[config.MoveData] = board.piecePickedUpLegalMoves
						if targetSquare == fromSquare: # register click toggle movement
							board.selectedSquare = fromSquare
							board.selectedSquareLegalMoves = fromLegalMoves.copy()
							board.piecePickedUp = (-1, -1)
							board.piecePickedUpLegalMoves = []
						else: # register drag movement
							board.selectedSquare = (-1, -1)
							board.selectedSquareLegalMoves = []
							valid = boardHandling.processMove(board = board, fromSquare = board.piecePickedUp, toSquare = targetSquare)
							_ = clockInstance.applyIncrement(sideToMove = board.SideToMove)
							if valid and board.pendingPromotion is None:
								board.syncBoardFlipStateToSideToMove()
							board.piecePickedUp = (-1, -1)
							board.piecePickedUpLegalMoves = []
							if valid and not board.hasFirstMoveHappened:
								board.hasFirstMoveHappened = True
								logger.info(msg = "Main: Starting clock after first move")
								clockInstance.setClockRunning(running = True)
					else:
						if board.selectedSquare != (-1, -1) and targetSquare != (-1, -1):
							legalMoveTargets: list[tuple[int, int]] = []
							for moveTarget in board.selectedSquareLegalMoves:
								legalMoveTargets.append(moveTarget.toSquare)
							if targetSquare in legalMoveTargets:
								valid = boardHandling.processMove(board = board, fromSquare = board.selectedSquare, toSquare = targetSquare)
								_ = clockInstance.applyIncrement(sideToMove = board.SideToMove)
								board.selectedSquare = (-1, -1)
								board.selectedSquareLegalMoves = []
							if valid and board.pendingPromotion is None:
								board.syncBoardFlipStateToSideToMove()
							if valid and not board.hasFirstMoveHappened:
								board.hasFirstMoveHappened = True
								logger.info(msg = "Main: Starting clock after first move")
								_ = clockInstance.setClockRunning(running = True)
							else:
								piece = board.Board[targetSquare[0]][targetSquare[1]][0]
								colour = board.Board[targetSquare[0]][targetSquare[1]][1]
								if piece != config.Piece.EMPTY and colour == board.SideToMove:
									row: int = targetSquare[0]
									col: int = targetSquare[1]
									board.selectedSquare = targetSquare
									board.selectedSquareLegalMoves = boardHandling.getLegalMovesForPiece(board = board, row = row, col = col)
								else:
									board.selectedSquare = (-1, -1)
									board.selectedSquareLegalMoves = []
						elif targetSquare != (-1, -1):
							piece = board.Board[targetSquare[0]][targetSquare[1]][0]
							colour = board.Board[targetSquare[0]][targetSquare[1]][1]
							if piece != config.Piece.EMPTY and colour == board.SideToMove:
								row = targetSquare[0]
								col = targetSquare[1]
								board.selectedSquare = targetSquare
								board.selectedSquareLegalMoves = boardHandling.getLegalMovesForPiece(board = board, row = row, col = col)
						board.piecePickedUp = (-1, -1)
						board.piecePickedUpLegalMoves = []


		if not board.gameState.gameOver and clockInstance.updateClock(sideToMove = board.SideToMove):
				board.gameState.gameOver = True                                                                                 
				board.gameState.winner = board.findOpposingColour(colour = board.SideToMove)                                    
				board.gameState.reason = config.GameOverReason.TIMEOUT                                                          
				board.piecePickedUp = (-1, -1)                                                                                  
				board.piecePickedUpLegalMoves = []                                                                              
				board.pendingPromotion = None                                                                                   
				logger.info(msg = f"Main: {board.SideToMove.name} ran out of time")
		renderThreadInstance.drawBoardBackground(screen = screen, board = board)
		#renderThreadInstance.debugRenderingMethod(board, screen)
		renderThreadInstance.renderBoard(screen = screen, board = board)
		promotionUIRects = renderThreadInstance.renderPromotionChoice(screen = screen, board = board)
		gameOverButtonRects = renderThreadInstance.renderGameOver(screen = screen, board = board)

		cursorToUse: int = pygame.SYSTEM_CURSOR_ARROW
		if hoveringOverButton:
			cursorToUse = pygame.SYSTEM_CURSOR_HAND
		elif board.pendingPromotion:
			for uiRect, _ in promotionUIRects:
				if uiRect.collidepoint(mouseX, mouseY):
					cursorToUse = pygame.SYSTEM_CURSOR_HAND
					break
		elif board.piecePickedUp != (-1, -1):
			cursorToUse = pygame.SYSTEM_CURSOR_HAND
		elif not board.gameState.gameOver:
			targetSquareTemp = board.getSquareUnderMousePosition()
			if targetSquareTemp is not None:
				row, col = targetSquareTemp
				piece, colour = board.Board[row][col]
				if piece != config.Piece.EMPTY and colour == board.SideToMove:
					cursorToUse = pygame.SYSTEM_CURSOR_CROSSHAIR
		elif board.gameState.gameOver:
			for buttonRect, _ in gameOverButtonRects:
				if buttonRect.collidepoint(mouseX, mouseY):
					cursorToUse = pygame.SYSTEM_CURSOR_HAND
					break

		if cursorToUse != currentCursor:
			pygame.mouse.set_cursor(cursorToUse)
			currentCursor = cursorToUse
		menuBarInstance.drawMenuBar(screen = screen)
		gameBarInstance.drawMenuBar(screen = screen)
		pygame.display.flip()
		_ = clock.tick(config.WindowDefaults.FPS.value)

	logger.info(msg = "Init: Exiting...")
	pygame.quit()

if __name__ == "__main__":
	main()
