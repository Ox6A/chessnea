import pytest

from chessnea.core import fen
from tests.helper import loadEPD

EPD_FEN_STRINGS: list[str] = [line.split(";")[0].strip() for line in loadEPD()]

@pytest.mark.parametrize(argnames = "fenStr", argvalues = EPD_FEN_STRINGS)
def testFENRoundTrip(fenStr: str) -> None:
	position = fen.importFENToPositionObject(fen = fenStr)
	fenStrBack = fen.exportPositionObjectToFEN(position = position)
	assert fenStr == fenStrBack