"""Defines the theme for the chess UI."""

from pathlib import Path

PIECE_SET_IDENTIFIER: str = "cburnett"

ASSETS_DIR: Path = Path(__file__).parent.parent.parent.parent / "assets"
ASSETS_PIECE_SET_DIR: Path = ASSETS_DIR / "pieces" / PIECE_SET_IDENTIFIER

# Lichess brown board: https://github.com/lichess-org/lila/blob/master/public/images/board/brown.png
SQUARE_WHITE: tuple[int, int, int] = (240, 217, 181)
SQUARE_BLACK: tuple[int, int, int] = (181, 136, 99)

# Lichess highlights: https://github.com/lichess-org/lila/blob/master/ui/lib/css/theme/board/_chessground.scss
# CSS opacity is converted to the nearest alpha value for our representation
SQUARE_HIGHLIGHT: tuple[int, int, int, int] = (20, 85, 30, 128) # Selected square @ 50% opacity
SQUARE_HIGHLIGHT_LAST_MOVE: tuple[int, int, int, int] = (155, 199, 0, 105) # Both fromSquare and toSquare @ 41% opacity

SQUARE_HIGHLIGHT_MOVE: tuple[int, int, int, int] = (20, 85, 30, 128) # Legal-move dots @ 50% opacity
SQUARE_HIGHLIGHT_MOVE_CAPTURE: tuple[int, int, int, int] = (20, 85, 0, 77) # Capture rings @ 30% opacity

# Check uses a radial gradient
SQUARE_HIGHLIGHT_CHECK_CENTRE: tuple[int, int, int, int] = (255, 0, 0, 255) # 0% radius
SQUARE_HIGHLIGHT_CHECK_INNER: tuple[int, int, int, int] = (231, 0, 0, 255) # 25% radius
SQUARE_HIGHLIGHT_CHECK_OUTER: tuple[int, int, int, int] = (169, 0, 0, 0) # 89% radius
SQUARE_HIGHLIGHT_CHECK_EDGE: tuple[int, int, int, int] = (158, 0, 0, 0) # 100% radius