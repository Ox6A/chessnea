from pathlib import Path

EPD_PATH: Path = Path(__file__).parent / "epd"
EPD_FILE = "chriswhittington.epd"

def loadEPD() -> list[str]:
    epdCompletePath: Path = Path.joinpath(EPD_PATH, EPD_FILE)
    epdList: list[str] = []
    for line in epdCompletePath.read_text(encoding = "utf_8").splitlines():
        epdList.append(line.strip())
    return epdList