"""Downloads UCI engines listed in assets/engines/engines.json from their respective URLs and saves them to the assets/engines directory."""

import logging
import stat
import tarfile
import urllib.request
import zipfile
from pathlib import Path

logger: logging.Logger = logging.getLogger(name = __name__)

ENGINES_DIR: Path = Path(__file__).parent.parent.parent.parent / "assets" / "engines"

def download(url: str, executablePathInArchive: str) -> Path:
	"""Downloads a UCI engine from the given URL and saves it to the specified path.

	Args:
		url (str): The URL to download the engine from.
		executablePath (str): The path the entry point executable is within the archive.

	Returns:
		Path: The path to the downloaded engine executable.
	"""
	archiveName: str = url.rsplit(sep = "/", maxsplit = 1)[-1]
	installDir: Path = ENGINES_DIR / archiveName.split(sep = ".", maxsplit = 1)[0]
	executablePath: Path = installDir / executablePathInArchive
	if executablePath.exists():
		logger.info(msg = f"Download: Engine already exists at {executablePath}, skipping download")
		return executablePath
	logger.info(msg = f"Download: Downloading engine from {url} to {installDir}")
	installDir.mkdir(parents = True, exist_ok = True)
	archivePath: Path = installDir / archiveName
	_ = urllib.request.urlretrieve(url = url, filename = archivePath)
	if archiveName.endswith(".zip"):
		with zipfile.ZipFile(file = archivePath) as zipFile:
			zipFile.extractall(path = installDir)
	elif archiveName.endswith((".tar.gz", ".tgz")):
		with tarfile.open(name = archivePath) as tarFile:
			tarFile.extractall(path = installDir)
	else:
		logger.error(msg = f"Download: Unsupported archive format for {archiveName}")
		raise ValueError(f"Unsupported archive format for {archiveName}")
	archivePath.unlink()
	_ = executablePath.chmod(mode = executablePath.stat().st_mode | stat.S_IEXEC)
	logger.info(msg = f"Download: Engine downloaded and extracted to {installDir}")
	return executablePath