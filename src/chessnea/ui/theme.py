from pathlib import Path

PIECE_SET_IDENTIFIER: str = "alpha"

ASSETS_DIR: Path = Path(__file__).parent.parent.parent.parent / "assets"
ASSETS_PIECE_SET_DIR: Path = ASSETS_DIR / "pieces" / PIECE_SET_IDENTIFIER

SQUARE_WHITE: tuple[int, int, int] = (240, 217, 181)
SQUARE_BLACK: tuple[int, int, int] = (181, 136, 99)