import pygame
import logging

from chessnea.board import BoardHandling
import chessnea.config as config
import chessnea.pgn as pgn

boardInstance: BoardHandling
logger: logging.Logger = logging.getLogger(name = __name__)

def loadBoardInUI(board: BoardHandling) -> None:
    global boardInstance
    boardInstance = board

def drawSmoothRoundedRect(surface: pygame.Surface, colour: tuple[int, int, int, int], rect: pygame.Rect, radius: int, width: int = 0) -> pygame.Rect:
    scaleFactor: int = 4
    enlargedSurface: pygame.Surface = pygame.Surface(
        size = (rect.width * scaleFactor, rect.height * scaleFactor), 
        flags = pygame.SRCALPHA)

    _ = pygame.draw.rect(
        surface = enlargedSurface, 
        color = colour, 
        rect = pygame.Rect(0, 0, rect.width * scaleFactor, rect.height * scaleFactor), 
        border_radius = radius * scaleFactor,
        width = width * scaleFactor)

    smoothSurface: pygame.Surface = pygame.transform.smoothscale(surface = enlargedSurface, size = (rect.width, rect.height))
    return surface.blit(source = smoothSurface, dest = rect)

def addStandardUIItems(menuBarInstance: "MenuBar") -> None:
    # Exit
    menuBarInstance.addMenuItem(
        item = config.MenuItem(
            name = "Exit", 
            itemType = config.ItemType.BUTTON, 
            children = None, 
            connector = ConnectorFunctions.exitGame,
            paddedRight = True))
    # Game Settings
    menuBarInstance.addMenuItem(
        item = config.MenuItem(
            name = "Game",
            itemType = config.ItemType.DROPDOWN,
            children = [
                config.MenuItem(
                    name = "New Game",
                    itemType = config.ItemType.BUTTON,
                    children = None,
                    connector = ConnectorFunctions.newGame
                ),
                config.MenuItem(
                    name = "Undo Move",
                    itemType = config.ItemType.BUTTON,
                    children = None,
                    connector = ConnectorFunctions.undoMove
                ),
                config.MenuItem(
                    name = "Import/Export FEN...",
                    itemType = config.ItemType.BUTTON,
                    children = None,
                    connector = ConnectorFunctions.handleFEN
                ),
                config.MenuItem(
                    name = "Import PGN...",
                    itemType = config.ItemType.BUTTON,
                    children = None,
                    connector = ConnectorFunctions.handlePGN
                ),
                config.MenuItem(
                    name = "Export PGN...",
                    itemType = config.ItemType.BUTTON,
                    children = None,
                    connector = ConnectorFunctions.handlePGN
                )
            ],
            connector = lambda: config.ReturnType.NORMAL))
    # Quick Settings
    menuBarInstance.addMenuItem(
        item = config.MenuItem(
            name = "Quick Settings",
            itemType = config.ItemType.DROPDOWN,
            children = [
                config.MenuItem(
                    name = "Auto Flip Board",
                    itemType = config.ItemType.TOGGLE,
                    children = None,
                    connector = ConnectorFunctions.setFlipBoard
                )
            ],
            connector = lambda: config.ReturnType.NORMAL))


class MenuBar():
    def __init__(self)  -> None:
        self.hidden: bool = False
        self.height: int = 50
        self.width: int = config.WindowDefaults.WINDOW_WIDTH.value
        self.hideTimeout: float = 0.5
        self.menuItems: list[config.MenuItem] = []
        self.fontRegular: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_REGULAR), size = 24)
        self.fontMedium: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 24)
        self.outlineWidth: int = 2

        # Padding
        self.paddingX: int = 16
        self.paddingY: int = 16
        self.itemHeight: int = 40
        self.itemGap: int = 0
        self.radius: int = 8

        # Dropdowns
        self.openItem: config.MenuItem | None = None
        self.dropdownItemHeight: int = 42
        self.dropdownWidth: int = 160
        self.dropdownOutlineWidth: int = 2

    def addMenuItem(self, item: config.MenuItem) -> None:
        self.menuItems.append(item)

    def checkIfHoveringOverMenuItem(self, mouseX: int, mouseY: int) -> config.MenuItem | None:
        if self.menuItems == [] or self.hidden:
            return None
        for i in self.menuItems:
            if i.rect and i.rect.collidepoint((mouseX, mouseY)):
                return i
            if i == self.openItem and i.children:
                for childItem in i.children:
                    if childItem.rect and childItem.rect.collidepoint((mouseX, mouseY)):
                        return childItem
        return None

    def runConnectorFunction(self, item: config.MenuItem) -> config.ReturnType:
        logger.info(msg = f"UI: Running connector function {item.connector.__name__}")
        return item.connector()

    def drawMenuBar(self, screen: pygame.Surface) -> None:
        if self.hidden:
            return
        mouseX, mouseY = pygame.mouse.get_pos()
        menuBarSurface: pygame.Surface = pygame.Surface(size = (self.width, self.height), flags = pygame.SRCALPHA)
        _ = menuBarSurface.fill(color = config.UIColours.SURFACE.value)

        offsetXForItemLeft: int = 0
        offsetXForItemRight: int = 0

        for item in self.menuItems:
            itemText: pygame.Surface = self.fontMedium.render(
                text = item.name, 
                antialias = True, 
                color = config.UIColours.TEXT_PRIMARY.value)
            itemWidth: int = itemText.get_width() + (self.paddingX * 2)
            itemRect: pygame.Rect
            if item.paddedRight:
                itemRect = pygame.Rect(self.width - offsetXForItemRight - itemWidth, 0, itemWidth, self.height)
            else:
                itemRect = pygame.Rect(offsetXForItemLeft, 0, itemWidth, self.height)
            isHovered: bool = itemRect.collidepoint(mouseX, mouseY)
            isPressed: bool
            if isHovered and pygame.mouse.get_pressed(num_buttons = 3)[0]:
                isPressed = True
            else:
                isPressed = False

            buttonColour: tuple[int, int, int, int]
            if isPressed:
                buttonColour = config.UIColours.ACTION_SELECTED.value
            elif isHovered and item.toggled:
                buttonColour = config.UIColours.ACTION_SELECTED_OVER_TOGGLED.value
            elif isHovered:
                buttonColour = config.UIColours.ACTION_HOVER.value
            elif item.toggled:
                buttonColour = config.UIColours.ACTION_TOGGLED.value
            else:
                buttonColour = config.UIColours.SURFACE.value

            _ = pygame.draw.rect(
                surface = menuBarSurface,
                color = buttonColour,
                rect = itemRect
            )
            item.rect = itemRect
            textRect: pygame.Rect = itemText.get_rect(center = itemRect.center)
            _ = menuBarSurface.blit(source = itemText, dest = textRect)
            if item.paddedRight:
                offsetXForItemRight += itemWidth + self.itemGap
                _ = pygame.draw.line(
                    surface = menuBarSurface,
                    color = config.UIColours.OUTLINE.value,
                    start_pos = (self.width - offsetXForItemRight, 0),
                    end_pos = (self.width - offsetXForItemRight, self.height),
                    width = self.outlineWidth
                )
                offsetXForItemRight += self.outlineWidth
            else:
                offsetXForItemLeft += itemWidth + self.itemGap
                _ = pygame.draw.line(
                    surface = menuBarSurface,
                    color = config.UIColours.OUTLINE.value,
                    start_pos = (offsetXForItemLeft, 0),
                    end_pos = (offsetXForItemLeft, self.height),
                    width = self.outlineWidth
                )
                offsetXForItemLeft += self.outlineWidth
            _ = pygame.draw.line(
                surface = menuBarSurface,
                color = config.UIColours.OUTLINE.value,
                start_pos = (0, self.height - 1),
                end_pos = (self.width, self.height - 1),
                width = 5
            )

            _ = screen.blit(source = menuBarSurface, dest = (0, 0))
            if item == self.openItem and item.children:
                dropdownX: int = itemRect.left - self.dropdownOutlineWidth
                dropdownY: int = self.height
                childItemRect: pygame.Rect
                maximumDropdownBoxWidth: int = 0
                dropdownOutlineOffset: int = self.dropdownOutlineWidth
                for childItem in item.children: # calculate largest dropdown width
                    dropdownWidth: int = max(itemRect.width, self.fontRegular.size(childItem.name)[0] + (self.paddingX * 2))
                    if maximumDropdownBoxWidth <= dropdownWidth:
                        maximumDropdownBoxWidth = dropdownWidth

                for childItem in item.children:
                    childItemRect = pygame.Rect(
                        dropdownX,
                        dropdownY - dropdownOutlineOffset,
                        maximumDropdownBoxWidth,
                        self.dropdownItemHeight
                    )
                    dropdownOutlineOffset += self.dropdownOutlineWidth
                    childItemColour: tuple[int, int, int, int]
                    childItemHovered: bool = childItemRect.collidepoint((mouseX, mouseY))
                    if childItem.toggled and childItemHovered:
                        childItemColour = config.UIColours.ACTION_SELECTED_OVER_TOGGLED.value
                    elif childItemHovered:
                        childItemColour = config.UIColours.ACTION_HOVER.value
                    elif childItem.toggled:
                        childItemColour = config.UIColours.ACTION_TOGGLED.value
                    else:
                        childItemColour = config.UIColours.SURFACE.value
                    _ = pygame.draw.rect(
                        surface = screen,
                        color = childItemColour,
                        rect = childItemRect
                    )
                    childItemText: pygame.Surface = self.fontRegular.render(
                        text = childItem.name,
                        antialias = True,
                        color = config.UIColours.TEXT_PRIMARY.value
                    )

                    childItemTextRect: pygame.Rect = childItemText.get_rect(
                        centery = childItemRect.centery,
                        left = childItemRect.left + self.paddingX
                    )
                    _ = screen.blit(source = childItemText, dest = childItemTextRect)
                    childItem.rect = childItemRect
                    dropdownY += self.dropdownItemHeight
                    _ = pygame.draw.rect(
                        surface = screen,
                        color = config.UIColours.OUTLINE.value,
                        rect = childItemRect,
                        width = self.dropdownOutlineWidth
                    )

class ConnectorFunctions():
    @staticmethod
    def exitGame() -> config.ReturnType:
        return config.ReturnType.QUIT_GAME

    @staticmethod
    def setFlipBoard() -> config.ReturnType:
        logging.info(msg = f"ConnectorFunctions: Toggled board flipping to value {not boardInstance.isBoardFlippingEnabled}")
        boardInstance.isBoardFlippingEnabled = not boardInstance.isBoardFlippingEnabled
        boardInstance.syncBoardFlipStateToSideToMove()
        return config.ReturnType.NORMAL

    @staticmethod
    def newGame() -> config.ReturnType:
        return boardInstance.resetBoard()

    @staticmethod
    def handleFEN() -> config.ReturnType:
        return config.ReturnType.NORMAL

    @staticmethod
    def handlePGN() -> config.ReturnType:
        pgnString: str = pgn.convertPositionHistoryToPGN(board = boardInstance)
        logger.info(msg = f"UI: {pgnString}")
        return config.ReturnType.NORMAL

    @staticmethod
    def undoMove() -> config.ReturnType:
        _ = boardInstance.undoMove()
        return _