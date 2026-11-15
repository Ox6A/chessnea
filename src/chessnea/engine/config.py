"""Loads the available UCI engines from assets/engines/engines.json"""

import json
import logging
import platform
import tarfile
import typing
import zipfile
from dataclasses import dataclass
from pathlib import Path

from chessnea.engine import download

logger: logging.Logger = logging.getLogger(name = __name__)

ENGINE_JSON_PATH: Path = Path(__file__).parent.parent.parent.parent / "assets" / "engines" / "engines.json"

@dataclass(frozen = True, slots = True)
class EngineConfig:
	"""Represents the settings for a UCI compatible engine.
	
	Attributes:
		name (str): The name of the engine.
		path (str): The path to the engine executable.
		options (dict[str, typing.Any]): A dictionary of engine options."""

	name: str
	path: str
	options: dict[str, str | int]

class EngineDownload(typing.TypedDict):
	"""Represents the download information for a UCI engine."""

	url: str
	executablePath: str

class EngineEntry(typing.TypedDict):
	"""Represents a single entry in the engines.json file."""

	name: str
	path: typing.NotRequired[str]
	options: typing.NotRequired[dict[str, str | int]]
	downloads: typing.NotRequired[dict[str, EngineDownload]]

class EngineFile(typing.TypedDict):
	"""Represents the structure of the engines.json file."""

	engines: list[EngineEntry]

def loadConfig(path: Path = ENGINE_JSON_PATH) -> dict[str, EngineConfig]:
	"""Loads the engine configurations from a JSON file.

	Args:
		path (Path): The path to the JSON file containing engine configurations.

	Returns:
		dict[str, EngineConfig]: A dictionary of engine configurations.
	"""

	if not path.exists():
		logger.error(msg = f"Init: Engine configuration file not found at {path}")
		return {}
	with path.open(encoding = "utf-8") as f:
		data: EngineFile = typing.cast(EngineFile, json.load(fp = f))

	engineConfigs: dict[str, EngineConfig] = {}
	for entry in data["engines"]:
		enginePath: str
		if "downloads" in entry:
			platformKey: str = f"{platform.system()}-{platform.machine()}"
			engineDownload: EngineDownload | None = entry["downloads"].get(platformKey)
			if engineDownload is None:
				logger.warning(msg = f"Init: No download information for engine {entry['name']} on platform {platformKey}")
				continue
			try:
				enginePath = str(download.download(url = engineDownload["url"], executablePathInArchive = engineDownload["executablePath"]))
			except (OSError, zipfile.BadZipFile, tarfile.TarError) as e:
				logger.error(msg = f"Init: Failed to download engine {entry['name']} from {engineDownload['url']}: {e}")
				continue
		elif "path" in entry:
			enginePath = entry["path"]
		else:
			logger.warning(msg = f"Init: No path or download information for engine {entry['name']}")
			continue
		engineConfig: EngineConfig = EngineConfig(
			name = entry["name"],
			path = enginePath,
			options = entry.get("options", {}),
		)
		engineConfigs[entry["name"]] = engineConfig
		logger.debug(msg = f"Init: Loaded engine configuration for {entry['name']}")
	return engineConfigs