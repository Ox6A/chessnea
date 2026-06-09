import pygame

import chessnea.config as config

class MenuBar():
    def __init__(self)  -> None:
        self.hidden: bool = False
        self.height: int = 64
        self.width: int = config.WIDTH
        self.hideTimeout: float = 0.5
        self.menuItems: list[config.MenuItem] = []
        self.fontRegular: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_REGULAR), size = 24)
        self.fontMedium: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 24)

        # Padding
        self.paddingX: int = 16
        self.paddingY: int = 16
        self.itemHeight: int = 40
        self.itemGap: int = 8
        self.radius: int = 15

    def addMenuItem(self, item: config.MenuItem) -> None:
        self.menuItems.append(item)

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
            itemWidth: int = itemText.get_width() + 28
            itemY: int = (self.height - self.itemHeight) // 2

            itemRect: pygame.Rect = pygame.Rect(offsetXForItem, itemY, itemWidth, self.itemHeight)
            isHovered: bool = itemRect.collidepoint(mouseX, mouseY)

            buttonColour: tuple[int, int, int, int]
            if isHovered:
                buttonColour = config.UIColours.PRIMARY_HOVER.value
            else:
                buttonColour = config.UIColours.PRIMARY.value

            _ = pygame.draw.rect(
                surface = menuBarSurface,
                color = buttonColour,
                rect = itemRect,
                border_radius = self.radius
            )

            textRect: pygame.Rect = itemText.get_rect(center = itemRect.center)
            _ = menuBarSurface.blit(source = itemText, dest = textRect)
            offsetXForItem += itemWidth + self.itemGap

        _ = screen.blit(source = menuBarSurface, dest = (0, 0))