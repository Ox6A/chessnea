import time
import math

import chessnea.config as config

class Clock():
    def __init__(self, startingTime: int = config.DEFAULT_STARTING_TIME, startingIncrement: int = config.DEFAULT_STARTING_INCREMENT) -> None:
        self.whiteTimeRemaining: float = float(startingTime)
        self.blackTimeRemaining: float = float(startingTime)
        self.clockRunning: bool = False
        self.lastUpdateTime: float = time.monotonic()
        self.increment: int = startingIncrement

    def resetClock(self) -> None:
        self.whiteTimeRemaining = float(config.DEFAULT_STARTING_TIME)
        self.blackTimeRemaining = float(config.DEFAULT_STARTING_TIME)
        self.clockRunning = False
        self.lastUpdateTime = time.monotonic()

    def toggleClock(self) -> None:
        self.clockRunning = not self.clockRunning
        self.lastUpdateTime = time.monotonic()

    def setClockRunning(self, running: bool) -> None:
        self.clockRunning = running
        self.lastUpdateTime = time.monotonic()

    def getTimeForPlayers(self) -> tuple[float, float]:
        return (self.whiteTimeRemaining, self.blackTimeRemaining)

    def getFormattedTimeForPlayers(self) -> tuple[str, str]:
        whiteRemainingInt: int = math.ceil(self.whiteTimeRemaining)
        blackRemainingInt: int = math.ceil(self.blackTimeRemaining)
        whiteMinutes: int = whiteRemainingInt // 60
        whiteSeconds: int = whiteRemainingInt % 60
        blackMinutes: int = blackRemainingInt // 60
        blackSeconds: int = blackRemainingInt % 60
        return (f"{whiteMinutes:02d}:{whiteSeconds:02d}", f"{blackMinutes:02d}:{blackSeconds:02d}")

    def updateClock(self, sideToMove: config.PieceColour) -> bool:
        timeToApply: float
        if self.clockRunning:
            currentTime: float = time.monotonic()
            elapsedTime: float = currentTime - self.lastUpdateTime
            if sideToMove == config.PieceColour.WHITE:
                timeToApply = (self.whiteTimeRemaining + self.increment) - elapsedTime
                if timeToApply <= 0:
                    self.whiteTimeRemaining = 0
                    self.clockRunning = False
                    return True
                self.whiteTimeRemaining = timeToApply
            else:
                timeToApply = (self.blackTimeRemaining + self.increment) - elapsedTime
                if timeToApply <= 0:
                    self.blackTimeRemaining = 0
                    self.clockRunning = False
                    return True
                self.blackTimeRemaining = timeToApply
            self.lastUpdateTime = currentTime
        return False