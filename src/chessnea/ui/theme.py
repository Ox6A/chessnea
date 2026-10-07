from pathlib import Path

PIECE_SET_IDENTIFIER: str = "cburnett"

ASSETS_DIR: Path = Path(__file__).parent.parent.parent.parent / "assets"
ASSETS_PIECE_SET_DIR: Path = ASSETS_DIR / "pieces" / PIECE_SET_IDENTIFIER

# Lichess brown board: https://github.com/lichess-org/lila/blob/master/public/images/board/brown.png
SQUARE_WHITE: tuple[int, int, int] = (240, 217, 181)
SQUARE_BLACK: tuple[int, int, int] = (181, 136, 99)

# Lichess highlights: https://github.com/lichess-org/lila/blob/master/ui/lib/css/theme/board/_chessground.scss
SQUARE_HIGHLIGHT: tuple[int, int, int, int] = (20, 85, 30, 128) # Selected square @ 50% opacity
SQUARE_HIGHLIGHT_MOVE: tuple[int, int, int, int] = (20, 85, 30, 128) # Legal-move dots @ 50% opacity
SQUARE_HIGHLIGHT_MOVE_CAPTURE: tuple[int, int, int, int] = (20, 85, 0, 77) # Capture move dots @ 30% opacity