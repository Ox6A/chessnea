import pygame

import chessnea.config as config

class MenuBar():
    def __init__(self)  -> None:
        self.hidden: bool = False
        self.height: int = 50 if config.HEIGHT > 200 else (config.HEIGHT // 4)
        self.width: int = config.WIDTH
        self.hideTimeout: float = 0.5
        self.menuItems: list[config.MenuItem] = []
        self.fontRegular: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_REGULAR), size = 24)
        self.fontMedium: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 24)

        # Padding
        self.paddingX: int = 24
        self.paddingY: int = 24

    def addMenuItem(self, item: config.MenuItem) -> None:
        self.menuItems.append(item)

    def drawMenuBar(self, screen: pygame.Surface) -> None:
        if not self.hidden:
            menuBarSurface: pygame.Surface = pygame.Surface(size = (self.width, self.height), flags = pygame.SRCALPHA)
            _ = pygame.draw.rect(surface = menuBarSurface, color = config.UIColours.PRIMARY.value, rect=(0, 0, self.width, self.height))

            itemXOffset: int = 0
            for itemIndex, item in enumerate[config.MenuItem](self.menuItems):
                itemText: pygame.Surface = self.fontMedium.render(
                    text = item.name, 
                    antialias = True, 
                    color = (255, 255, 255))
                itemWidthOffset: int = itemText.get_width() + self.paddingX
                _ = menuBarSurface.blit(
                    source = itemText, 
                    dest = (itemXOffset + self.paddingX, self.height // 2 - itemText.get_height() // 2))
                itemXOffset += itemWidthOffset
            _ = screen.blit(source = menuBarSurface, dest = (0, 0))