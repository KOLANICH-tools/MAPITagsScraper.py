import re
from ast import literal_eval

from ..consts import GitHubRawBase
from ..KSEnumValue import KSEnumValue
from ..nameNormalizer import canonicalizeOrigName, convertName
from ..Source import Source

parserGenTagRecordRx = re.compile(r"\s*\{\s*(0x[\da-f]+)\s*,\s*(0x[\da-f]+)\s*,\s*L?\"(\w+)\"\s*\}\s*(?:,\s*)")


def parseGenTagArrayLines(headerFileLines):
	for l in headerFileLines:
		m = parserGenTagRecordRx.match(l)
		if m:
			yield m.groups()


def KSEnumValueFromGenTagArrayTriple(valueStr, typeStr, nameStr):
	origName = canonicalizeOrigName(nameStr)
	name = convertName(origName)
	rawValue = literal_eval(valueStr)
	value = rawValue >> (8 * 2)

	return KSEnumValue(name, value, origName, None, None, None)


class GenTagArraySource(Source):
	__slots__ = ()

	def parseValuesFromSrc(self, src):
		return [KSEnumValueFromGenTagArrayTriple(*el) for el in parseGenTagArrayLines(src.splitlines())]


genTagArray = GenTagArraySource("genTagArray", "genTagArray.h", GitHubRawBase + "/stephenegriffin/mfcmapi/151856e6ef5af42368a49a1340060aa58d981e8e/core/interpret/genTagArray.h", "MIT")
