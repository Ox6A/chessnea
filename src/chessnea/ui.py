import pygame

import chessnea.config as config

def drawSmoothRoundedRect(surface: pygame.Surface, colour: tuple[int, int, int, int], rect: pygame.Rect, radius: int) -> pygame.Rect:
    scaleFactor: int = 4
    enlargedSurface: pygame.Surface = pygame.Surface(
        size = (rect.width * scaleFactor, rect.height * scaleFactor), 
        flags = pygame.SRCALPHA)

    _ = pygame.draw.rect(
        surface = enlargedSurface, 
        color = colour, 
        rect = pygame.Rect(0, 0, rect.width * scaleFactor, rect.height * scaleFactor), 
        border_radius = radius * scaleFactor)

    smoothSurface: pygame.Surface = pygame.transform.smoothscale(surface = enlargedSurface, size = (rect.width, rect.height))
    return surface.blit(source = smoothSurface, dest = rect)


class MenuBar():
    def __init__(self)  -> None:
        self.hidden: bool = True
        self.height: int = 50
        self.width: int = config.WIDTH
        self.hideTimeout: float = 0.5
        self.menuItems: list[config.MenuItem] = []
        self.fontRegular: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_REGULAR), size = 24)
        self.fontMedium: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 24)

        # Padding
        self.paddingX: int = 16
        self.paddingY: int = 16
        self.itemHeight: int = 40
        self.itemGap: int = 0
        self.radius: int = 8

    def addMenuItem(self, item: config.MenuItem) -> None:
        self.menuItems.append(item)

    def checkIfHoveringOverMenuItem(self, mouseX: int, mouseY: int) -> pygame.Rect | None:
        if self.menuItems == [] or self.hidden == True:
            return None
        for i in self.menuItems:
            if not i.rect:
                continue
            if i.rect.collidepoint((mouseX, mouseY)):
                return i.rect
        return None

    def runConnectorFunction(self, item: config.MenuItem) -> None:
        _ = item.connector()

    def drawMenuBar(self, screen: pygame.Surface) -> None:
        if self.hidden:
            return
        mouseX, mouseY = pygame.mouse.get_pos()
        menuBarSurface: pygame.Surface = pygame.Surface(size = (self.width, self.height), flags = pygame.SRCALPHA)
        _ = menuBarSurface.fill(color = config.UIColours.SURFACE.value)

        offsetXForItem: int = 0

        for item in self.menuItems:
            itemText: pygame.Surface = self.fontMedium.render(
                text = item.name, 
                antialias = True, 
                color = config.UIColours.TEXT_PRIMARY.value)
            itemWidth: int = itemText.get_width() + (self.paddingX * 2)
            itemRect: pygame.Rect
            if item.paddedRight:
                itemRect = pygame.Rect(self.width - offsetXForItem - itemWidth, 0, itemWidth, self.height)
            else:
                itemRect = pygame.Rect(offsetXForItem, 0, itemWidth, self.height)
            isHovered: bool = itemRect.collidepoint(mouseX, mouseY)
            isPressed: bool
            if isHovered and pygame.mouse.get_pressed(num_buttons = 3)[0]:
                isPressed = True
            else:
                isPressed = False

            buttonColour: tuple[int, int, int, int]
            if isPressed:
                buttonColour = config.UIColours.ACTION_SELECTED.value
            elif isHovered:
                buttonColour = config.UIColours.ACTION_HOVER.value
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
            offsetXForItem += itemWidth + self.itemGap
            if item.paddedRight:
                _ = pygame.draw.line(
                    surface = menuBarSurface,
                    color = config.UIColours.OUTLINE.value,
                    start_pos = (self.width - offsetXForItem, 0),
                    end_pos = (self.width - offsetXForItem, self.height),
                    width = 2
                )
            else:
                _ = pygame.draw.line(
                    surface = menuBarSurface,
                    color = config.UIColours.OUTLINE.value,
                    start_pos = (offsetXForItem, 0),
                    end_pos = (offsetXForItem, self.height),
                    width = 2
                )

        _ = pygame.draw.line(
            surface = menuBarSurface,
            color = config.UIColours.OUTLINE.value,
            start_pos = (0, self.height - 1),
            end_pos = (self.width, self.height - 1),
            width = 5
        )

        _ = screen.blit(source = menuBarSurface, dest = (0, 0))

class ConnectorFunctions():
    @staticmethod
    def exitGame() -> bool:
        exit()