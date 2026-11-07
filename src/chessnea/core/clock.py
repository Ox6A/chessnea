"""Functions necessary for the game clock to work."""

DEFAULT_STARTING_TIME_SECONDS: int = 600
DEFAULT_INCREMENT_SECONDS: int = 5

import math
import time

from chessnea.core import types


class Clock:
    """A class representing a chess clock."""

    def __init__(self, startingTime: int = DEFAULT_STARTING_TIME_SECONDS, increment: int = DEFAULT_INCREMENT_SECONDS) -> None:
        self.startingTime: int = startingTime
        self.increment: int = increment
        self.timeRemaining: dict[types.PieceColour, float] = {}
        self.isRunning: bool = False
        self.lastUpdate: float = 0.0
        self.resetClock()

    def resetClock(self) -> None:
        """Resets the clock to its initial state.
        
        Args:
            None
        Returns:
            None
        """

        self.timeRemaining = {
            types.PieceColour.WHITE: float(self.startingTime),
            types.PieceColour.BLACK: float(self.startingTime)
        }
        self.isRunning = False
        self.lastUpdate = time.monotonic()

    def setClockState(self, isRunning: bool) -> None:
        """Sets the clock's running state.
        
        Args:
            isRunning: True if the clock should be running, False otherwise.
        Returns:
            None
        """

        self.isRunning = isRunning
        self.lastUpdate = time.monotonic()

    def updateClock(self, sideToMove: types.PieceColour) -> bool:
        """Updates the clock based on the time elapsed since the last update.
        
        Args:
            sideToMove: The side that is to move.
        Returns:
            bool: True if the player has run out of time, False otherwise.
        """

        if not self.isRunning:
            return False
        currentTime = time.monotonic()
        self.timeRemaining[sideToMove] -= (currentTime - self.lastUpdate)
        self.lastUpdate = currentTime
        if self.timeRemaining[sideToMove] <= 0:
            self.timeRemaining[sideToMove] = 0.0
            self.isRunning = False
            return True
        return False

    def applyClockIncrement(self, sideToMove: types.PieceColour) -> None:
        """Applies the increment to the clock for the given side.
        
        Args:
            sideToMove: The side that is to move.
        Returns:
            None
        """
        if self.isRunning:
            self.timeRemaining[sideToMove] += self.increment

    def getTimeAsString(self, sideToMove: types.PieceColour) -> str:
        """Returns the time remaining for the given side as a formatted string.

        >= 10 seconds shows as MM:SS
        < 10 seconds shows as SS.th
        
        Args:
            sideToMove: The side for which to get the time remaining.
        Returns:
            str: The time remaining as a string in the required format.
        """
        
        timeRemaining: float = self.timeRemaining[sideToMove]
        if timeRemaining < 10:
            hundredths: int = math.floor(timeRemaining * 100)
            return f"{hundredths // 100:02d}.{hundredths % 100:02d}"
        totalSeconds = math.ceil(self.timeRemaining[sideToMove])
        minutes = totalSeconds // 60
        seconds = totalSeconds % 60
        return f"{minutes:02d}:{seconds:02d}"