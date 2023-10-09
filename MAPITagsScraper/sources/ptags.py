from ..consts import GitHubRawBase
from ..KSEnumValue import KSEnumValue
from ..Source import Source
from ..nameNormalizer import prepareNamesAndOrigIds

import ast
import re
import typing

import simpleeval

defineRx = re.compile("^\\s*#define\\s+(?P<name>\w+)\\s+(?P<payload>.+)\\s*$")
removeEndNoRx = re.compile("^(\w+?)(?:_\d+)?$")

evaluator = simpleeval.SimpleEval()
allowedNodeTypes = {ast.Constant, ast.Num, ast.UnaryOp, ast.BinOp, ast.BinOp, ast.Compare, ast.Expr, ast.Tuple, ast.BitOr}
evaluator.nodes = {nt: cb for nt, cb in evaluator.nodes.items() if nt in allowedNodeTypes}


def parseValueFromSourceEnumStr(l: str) -> typing.Optional[KSEnumValue]:
	m = defineRx.match(l)
	if m:
		origId = removeEndNoRx.match(m.group("name")).group(1)
		payload = m.group("payload")
		ppld = payload
		payload = payload.rsplit(")", 1)
		typ = None
		valueRaw = None

		if len(payload) > 1:
			payload = "".join(payload[:-1])
			if payload:
				v = payload.replace("PROP_TAG(", "").replace("(ULONG)", "").split(",")
				if len(v) == 2:
					typ, valueRaw = v
				else:
					print(v)
			else:
				print(l)
		else:
			valueRaw = payload[0]

		if valueRaw:
			try:
				value = evaluator.eval(valueRaw)
			except simpleeval.FeatureNotAvailable:
				pass
			else:
				# typ = evaluator.eval(typ)  # not needed
				origId, name = next(zip(*prepareNamesAndOrigIds([origId])))
				return KSEnumValue(name, value, origId, None, None, None)


class PTagsSource(Source):
	__slots__ = ()

	def parseValuesFromSrc(self, src: str) -> typing.Iterator[KSEnumValue]:
		for l in src.splitlines():
			if not l.startswith("// In File:"):
				v = parseValueFromSourceEnumStr(l)
				if v:
					yield v
				else:
					print("ptags line not parsed:", l)


ptags = PTagsSource("ptags", "ptags.h", GitHubRawBase + "dbremner/pstviewtool/52f59893ad4390358053541b0257b4a7f2767024/ptags.h", "Likely Apache. The repo contains no license, but the news (https://www.infoq.com/news/2010/05/Outlook-PST-View-Tool-and-SDK/, also https://web.archive.org/web/20140704101722/http://www.microsoft.com/en-us/news/press/2010/may10/05-24psttoolspr.aspx) claim that this tool and https://github.com/enrondata/pstsdk were published under Apache. Looks plausible since both software were authored by Terry Mahaffey (psviewtool has user name terrymah (though without a proper email) in git commits, likely the same guy as https://github.com/terrymah, pstsdk has the lines `author Terry Mahaffey`)")
