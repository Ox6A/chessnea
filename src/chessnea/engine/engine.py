"""Runs a UCI chess engine in a thread"""

import logging
import queue
import subprocess
import threading
import typing

from chessnea.core import types
from chessnea.core.clock import Clock
from chessnea.engine.config import EngineConfig

logger: logging.Logger = logging.getLogger(name = __name__)

class Engine:
	def __init__(self, config: EngineConfig) -> None:
		self.name: str = config.name
		self.searching: bool = False
		self.process: subprocess.Popen[str] = subprocess.Popen(
			args = [config.path],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.DEVNULL,
			text = True,
			bufsize = 1
		)
		self.outputQueue: queue.Queue[str] = queue.Queue()
		self.outputThread: threading.Thread = threading.Thread(
			target = self.readOutput,
			daemon = True
		)
		self.outputThread.start()
		self.sendCommand(command = "uci")
		_ = self.blockUntilOutput(prefix = "uciok")
		for optionName, optionValue in config.options.items():
			self.sendCommand(command = f"setoption name {optionName} value {optionValue}")
		self.blockUntilReady()
		
	def readOutput(self) -> None:
		"""Reads the output from the engine's stdout and puts it in a queue.
		
		Raises:
			AssertionError: If the engine's stdout is not available.
		"""
		assert self.process.stdout is not None
		output: typing.TextIO = typing.cast(typing.TextIO, self.process.stdout)
		for line in output:
			logger.debug(msg = f"UCI: Output from {self.name}: {line.strip()}")
			self.outputQueue.put(item = line.strip())
	
	def sendCommand(self, command: str) -> None:
		"""Sends a command to the engine's stdin.
		
		Args:
			command (str): The command to send to the engine.
		Raises:
			AssertionError: If the engine's stdin is not available.
		"""
		assert self.process.stdin is not None
		input: typing.TextIO = typing.cast(typing.TextIO, self.process.stdin)
		_ = input.write(f"{command}\n")
		input.flush()
		logger.debug(msg = f"UCI: Command sent to {self.name}: {command}")

	def blockUntilOutput(self, prefix: str, timeoutSeconds: float = 10.0) -> str:
		"""Blocks until the expected output is received from the engine.
		
		Args:
			prefix (str): The expected output prefix to wait for.
			timeoutSeconds (float): The maximum time to wait for the output.
		Returns:
			str: The output from the engine.
		"""
		while True:
			output: str = self.outputQueue.get(timeout = timeoutSeconds)
			if output.startswith(prefix):
				return output

	def blockUntilReady(self) -> None:
		"""Blocks until the engine is ready to receive commands."""
		self.sendCommand(command = "isready")
		_ = self.blockUntilOutput(prefix = "readyok")

	def newGame(self) -> None:
		"""Starts a new game in the engine."""
		self.cancelSearch()
		self.sendCommand(command = "ucinewgame")
		self.blockUntilReady()

	def startSearch(self, startFEN: str, UCIMoves: list[str], clock: Clock) -> None:
		position: str = f"position fen {startFEN}"
		if UCIMoves:
			position += f" moves {' '.join(UCIMoves)}"
		self.sendCommand(command = position)
		whiteMs, blackMs = clock.timeRemaining[types.PieceColour.WHITE] * 1000, clock.timeRemaining[types.PieceColour.BLACK] * 1000
		incrementMs = clock.increment * 1000
		self.sendCommand(command = f"go wtime {int(whiteMs)} btime {int(blackMs)} winc {int(incrementMs)} binc {int(incrementMs)}")
		self.searching = True

	def cancelSearch(self) -> None:
		"""Cancels the current search in the engine."""
		if self.searching:
			self.sendCommand(command = "stop")
			_ = self.blockUntilOutput(prefix = "bestmove")
			self.searching = False
	
	def pollEngineMove(self) -> str | None:
		"""Polls the engine for the best move found so far.
		
		Returns:
			str | None: The best move found by the engine, or None if no move is found.
		"""
		while True:
			try:
				output: str = self.outputQueue.get_nowait()
				if output.startswith("bestmove"):
					self.searching = False
					return output.split()[1]
			except queue.Empty:
				return None

	def close(self) -> None:
		"""Closes the engine process."""
		try:
			self.sendCommand(command = "quit")
			_ = self.process.wait(timeout = 5)
		except (OSError, subprocess.TimeoutExpired):
			logger.warning(msg = f"UCI: Engine {self.name} did not terminate gracefully. Killing process.")
			self.process.kill()
		logger.info(msg = f"UCI: Engine {self.name} closed.")