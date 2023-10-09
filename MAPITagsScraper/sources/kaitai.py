import typing
from pathlib import Path

from ..KSEnumValue import KSEnumValue
from ..Source import ProtoSource
from ..utils import sortedDictByKey
from ..utils.yaml import dumpYaml


def KSEnumValueFromKSEnumDictKeyValuePair(key, value):
	if isinstance(value, str):
		oid = []
		doc = None
		iD = value
	else:
		oid = value.get("-orig-id", [])
		if isinstance(oid, str):
			oid = [oid]
		doc = value.get("doc", None)
		iD = value["id"]

	return KSEnumValue(iD, key, oid, doc)


class SerializingContext:
	__slots__ = ("parent", "ks", "enums", "enum", "meta", "docRef")

	def __init__(self, parent, src):
		self.parent = parent

		import ruamel.yaml

		y = ruamel.yaml.YAML(typ="rt")
		ks = y.load(src)
		if ks is None:  # empty file, usually when serialization has failed
			ks = y.load(parent.getTemplateFilePath().read_text("utf-8"))
		self.ks = ks

		meta = ks.get("meta", None)
		if meta is None:
			ks["meta"] = meta = ruamel.yaml.comments.CommentedMap()
		self.meta = meta

		meta["id"] = self.parent.traditionalFileNameStem

		docRef = ks.get("doc-ref", None)
		if meta is None:
			ks["doc-ref"] = docRef = ruamel.yaml.comments.CommentedSeq()
		self.docRef = docRef

		e = ks.get("enums", None)
		if e is None:
			ks["enums"] = e = ruamel.yaml.comments.CommentedMap()
		self.enums = e

		enumName = self.parent.enumName
		ee = e.get(enumName, None)
		if ee is None:
			e[enumName] = ee = ruamel.yaml.comments.CommentedMap()

		self.enum = ee

	def sortByKey(self):
		self.enums[self.parent.enumName] = t = sortedDictByKey(self.enum)

	def parseValues(self):
		return [KSEnumValueFromKSEnumDictKeyValuePair(k, v) for k, v in self.enum.items()]

	@classmethod
	def intoKSEnumDict(cls, ksEnumValue: KSEnumValue, enumInstanceDict, merge=True):
		oid = ksEnumValue.origIds
		enumInstanceDict["id"] = ksEnumValue.id

		if oid:
			if len(oid) == 1:
				oid = oid[0]

			enumInstanceDict["-orig-id"] = oid
		else:
			if merge and "-orig-id" in enumInstanceDict:
				del enumInstanceDict["-orig-id"]

		if ksEnumValue.doc:
			enumInstanceDict["doc"] = ksEnumValue.doc
		else:
			if merge and "doc" in enumInstanceDict:
				del enumInstanceDict["doc"]

		if ksEnumValue.companion:
			enumInstanceDict["-companion"] = ksEnumValue.companion

		if ksEnumValue.subject:
			enumInstanceDict["-subject"] = ksEnumValue.subject

	def decorateInt(self, i):
		import ruamel.yaml

		return ruamel.yaml.scalarint.HexInt(i, width=self.parent.hexWidth)

	def insertSource(self, uri, license):
		# ruamel.yaml.tokens.CommentToken(value, start_mark, end_mark)
		idx = len(self.docRef)
		self.docRef.append(uri)
		self.docRef.yaml_add_eol_comment(license, idx, column=0)

	def enumValues2KSEnumDict(self, enumValues: typing.Iterable[KSEnumValue]):
		import ruamel.yaml

		for el in enumValues:
			k = self.decorateInt(el.value)
			v = self.enum.get(k, None)
			if v is None:
				v = ruamel.yaml.comments.CommentedMap()
				self.enum[k] = v

			self.__class__.intoKSEnumDict(el, v, merge=True)

	def dump(self, outputDir):
		dumpYaml(self.ks, outputDir / self.parent.traditionalFileName)


class KaitaiSource(ProtoSource):
	__slots__ = ("enumName", "traditionalFileNameStem", "hexWidth")

	def __init__(self, name, traditionalFileNameStem, enumName, hexWidth):
		self.traditionalFileNameStem = traditionalFileNameStem
		super().__init__(name, traditionalFileNameStem + ".ksy")
		self.enumName = enumName
		self.hexWidth = hexWidth

	def _getCtxFromSrc(self, src):
		return SerializingContext(self, src)

	def _getCtxFromDir(self, fileDir: Path):
		return self._getCtxFromSrc(self.fetch(fileDir))

	def parseValuesFromSrc(self, src):
		return self._getCtxFromSrc(src).parseValues()

	def fetch(self, fileDir: Path) -> str:
		ksyFile = fileDir / self.traditionalFileName
		ksyFileToLoad = None
		if ksyFile.exists():
			ksyFileToLoad = ksyFile
		else:
			ksyFileToLoad = self.getTemplateFilePath()

		return ksyFileToLoad.read_text(encoding="utf-8")

	def getTemplatefileName(self):
		return self.traditionalFileNameStem + ".template.ksy"

	def getTemplateFilePath(self):
		return Path(__file__).parent.parent / self.getTemplatefileName()


_kaitai = KaitaiSource("_kaitai", "mapi_tags", "tag", 4)
