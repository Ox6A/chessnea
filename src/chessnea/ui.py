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
        self.hidden: bool = False
        self.height: int = 64
        self.width: int = config.WIDTH
        self.hideTimeout: float = 0.5
        self.menuItems: list[config.MenuItem] = []
        self.fontRegular: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_REGULAR), size = 24)
        self.fontMedium: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 24)
        self.itemRectsForCollision: list[pygame.Rect] = []

        # Padding
        self.paddingX: int = 16
        self.paddingY: int = 16
        self.itemHeight: int = 40
        self.itemGap: int = 8
        self.radius: int = 8

    def addMenuItem(self, item: config.MenuItem) -> None:
        self.menuItems.append(item)

    def checkIfHoveringOverMenuItem(self, mouseX: int, mouseY: int) -> bool:
        for i in self.itemRectsForCollision:
            if i.collidepoint((mouseX, mouseY)):
                return True
        return False

    def drawMenuBar(self, screen: pygame.Surface) -> None:
        if self.hidden:
            return
        mouseX, mouseY = pygame.mouse.get_pos()
        menuBarSurface: pygame.Surface = pygame.Surface(size = (self.width, self.height), flags = pygame.SRCALPHA)
        _ = menuBarSurface.fill(color = config.UIColours.PRIMARY_LIGHT.value)

        offsetXForItem: int = self.paddingX

        for item in self.menuItems:
            itemText: pygame.Surface = self.fontMedium.render(
                text = item.name, 
                antialias = True, 
                color = config.UIColours.TEXT_ON_PRIMARY.value)
            itemWidth: int = itemText.get_width() + (self.paddingX * 2)
            itemY: int = (self.height - self.itemHeight) // 2

            itemRect: pygame.Rect = pygame.Rect(offsetXForItem, itemY, itemWidth, self.itemHeight)
            isHovered: bool = itemRect.collidepoint(mouseX, mouseY)

            buttonColour: tuple[int, int, int, int]
            if isHovered:
                buttonColour = config.UIColours.PRIMARY_HOVER.value
            else:
                buttonColour = config.UIColours.PRIMARY.value

            rectToSave = drawSmoothRoundedRect(
                surface = menuBarSurface,
                colour = buttonColour,
                rect = itemRect,
                radius = self.radius
            )
            self.itemRectsForCollision.append(rectToSave)
            textRect: pygame.Rect = itemText.get_rect(center = itemRect.center)
            _ = menuBarSurface.blit(source = itemText, dest = textRect)
            offsetXForItem += itemWidth + self.itemGap

        _ = pygame.draw.line(
            surface = menuBarSurface,
            color = config.UIColours.OUTLINE.value,
            start_pos = (0, self.height - 1),
            end_pos = (self.width, self.height - 1),
            width = 5
        )

        _ = screen.blit(source = menuBarSurface, dest = (0, 0))