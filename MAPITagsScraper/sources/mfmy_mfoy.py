from ..consts import GitHubRawBase
from ..KSEnumValue import KSEnumValue
from ..Source import Source
from ..nameNormalizer import prepareNamesAndOrigIds

MFMRepo = "hfig/MAPI"
MFMRepoSchemaPath = "src/MAPI/Schema/"
MFMRepoBranch = "master"

MFMRepoSchemaBase = GitHubRawBase + MFMRepo + "/" + MFMRepoBranch + "/" + MFMRepoSchemaPath


class MFMSource(Source):
	__slots__ = ()

	def processItem(self, k, v_origIds):
		v_origIds, names = prepareNamesAndOrigIds(v_origIds, True)
		return KSEnumValue("_or_".join(names), k, v_origIds, None, None, None)

	def processItems(self, enumValuesDictItems):
		for k, v in enumValuesDictItems:
			yield self.processItem(k, v)

	def parseValuesFromYaml(self, y):
		raise NotImplementedError

	def parseValuesFromSrc(self, src):
		import ruamel.yaml

		y = ruamel.yaml.YAML(typ="safe")
		y = y.load(src)
		return self.parseValuesFromYaml(y)


class MFMYSource(MFMSource):
	__slots__ = ()

	def parseValuesFromYaml(self, y):
		itemsToProcess = (((int(k, 16), v[0:1]) for k, v in y.items()))
		return self.processItems(itemsToProcess)


from icecream import ic

class MFOYSource(MFMSource):
	__slots__ = ()

	def parseValuesFromYaml(self, y):
		del y["PS_PUBLIC_STRINGS"]
		for typeName, enumValuesDict in y.items():
			itemsToProcess = ((k, (v,)) for k, v in enumValuesDict.items())
			yield from self.processItems(itemsToProcess)


mfoy = MFOYSource("mfoy", "MapiFieldsOther.yaml", MFMRepoSchemaBase + "MapiFieldsOther.yaml", "MIT")
mfmy = MFMYSource("mfmy", "MapiFieldsMessage.yaml", MFMRepoSchemaBase + "MapiFieldsMessage.yaml", "MIT")
