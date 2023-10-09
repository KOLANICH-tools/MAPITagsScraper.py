from pathlib import Path

from plumbum import cli

from .consts import defaultCacheDir
from .sources import sources


sourcesParamValidator = cli.Set(*sources, case_sensitive=True, csv=True)


class CLI(cli.Application):
	"""A tool to generate a Kaitai Struct spec with MAPI tags enum"""


@CLI.subcommand("fetch")
class FetchCLI(cli.Application):
	"""Just downloads the files into a cache dir"""

	def main(self, sourceNames: sourcesParamValidator, cacheDir: str = defaultCacheDir):
		cacheDir = Path(cacheDir)

		for sourceName in sourceNames:
			s = sources[sourceName]
			print("Ensuring", s)
			s.fetch(cacheDir)


@CLI.subcommand("convert")
class ConvertCLI(cli.Application):
	"""Converts the files into Kaitai Struct spec with tag definitions"""

	def main(self, sourceNames: sourcesParamValidator, cacheDir: str = defaultCacheDir):
		cacheDir = Path(cacheDir)

		from . import fullPipeline

		sourcesList = [sources[sourceName] for sourceName in sourceNames]

		fullPipeline(Path("."), sourcesList, cacheDir)


@CLI.subcommand("check")
class CheckCLI(cli.Application):
	"""Just a sanity check to guide manual name assigning"""

	def main(self, cacheDir: str = defaultCacheDir):
		from pprint import pprint

		from . import getTagsWithNonUniqueNames

		cacheDir = Path(cacheDir)
		pprint(getTagsWithNonUniqueNames(cacheDir))


if __name__ == "__main__":
	CLI.run()
