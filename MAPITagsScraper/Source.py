from pathlib import Path


def cachedFetchFile(cacheFile, uri):
	cacheFile.parent.mkdir(parents=True, exist_ok=True)

	if cacheFile.is_file():
		return cacheFile.read_bytes()

	import httpx

	data = httpx.get(uri).content
	cacheFile.write_bytes(data)
	return data


class ProtoSource:
	__slots__ = ("name", "traditionalFileName")

	def __init__(self, name, traditionalFileName):
		self.name = name
		self.traditionalFileName = traditionalFileName

	def fetch(self, fileDir: Path) -> str:
		return (fileDir / self.traditionalFileName).read_text(encoding="utf-8")

	def parseEnumValues(self, fileDir: Path):
		return self.parseValuesFromSrc(self.fetch(fileDir))

	def parseValuesFromSrc(self, src):
		raise NotImplementedError

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(getattr(self, k)) for k in __class__.__slots__) + ")"


class Source(ProtoSource):
	__slots__ = ("uri", "license")

	def __init__(self, name, cachedFileName, uri, license):
		super().__init__(name, cachedFileName)
		self.uri = uri
		self.license = license

	@property
	def cachedFileName(self):
		return self.traditionalFileName

	def fetch(self, cacheDir: Path) -> str:
		return cachedFetchFile(cacheDir / self.cachedFileName, self.uri).decode("utf-8")

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(getattr(self, k)) for k in (__class__.__slots__ + super().__slots__)) + ")"
