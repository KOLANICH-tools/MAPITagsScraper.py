from ..consts import GitHubRawBase
from ..KSEnumValue import KSEnumValue
from ..Source import Source
from ..nameNormalizer import prepareNamesAndOrigIds
from .ptags import parseValueFromSourceEnumStr
from .OxProps import SectionDict2Enum

from typed_ast import ast27
from typed_ast import ast3 as ast
from typed_ast.conversions import py2to3
import re
from ast import literal_eval

names1 = {"temporary_private_tags_struct", "knownpropsets", "extra_private_tags_struct", "temporary_private_tags", "temporary_private_tags_struct"}


def correctLiteralEval(v):
	if isinstance(v, dict):
		return {correctLiteralEval(k): correctLiteralEval(v) for k, v in v.items()}
	elif isinstance(v, list):
		return [correctLiteralEval(el) for el in v]
	elif isinstance(v, bytes):
		return v.decode("utf-8")
	return v


def correctedLiteralEval(a):
	return correctLiteralEval(ast.literal_eval(a))


def extractGroup1OfNames(sourceAST):
	res = {}
	for ael in sourceAST.body:
		if isinstance(ael, ast.Assign) and len(ael.targets) == 1:
			nm = ael.targets[0].id
			if nm in names1:
				res[nm] = correctedLiteralEval(ael.value)
	return res


def if1LevelAttr(firstLevel: str, secondLevel: str):
	def res(funcExpr) -> bool:
		# ic(firstLevel, secondLevel, isinstance(funcExpr, ast.Attribute), isinstance(funcExpr.value, ast.Name), funcExpr.value.id == firstLevel, funcExpr.attr == secondLevel)
		return isinstance(funcExpr, ast.Attribute) and isinstance(funcExpr.value, ast.Name) and funcExpr.value.id == firstLevel and funcExpr.attr == secondLevel

	return res


ifPropertiesAppend = if1LevelAttr("properties", "append")
ifAltnamelinesAppend = if1LevelAttr("altnamelines", "append")
ifFWrite = if1LevelAttr("f", "write")
ifStrLjust = if1LevelAttr("string", "ljust")


class OpenChangeSectionDict2Enum(SectionDict2Enum):
	__slots__ = ()

	CAN_NAME = "CanonicalName"
	PROP_ID_NAME = "PropertyId"
	ALT_NAMES_NAME = "AlternateNames"


sectDict2Enum = OpenChangeSectionDict2Enum()


def parsePropertiesAppend(xprs):
	for el in xprs:
		v = el.value
		if ifPropertiesAppend(v.func):
			r = correctedLiteralEval(v.args[0])
			origIds, value, doc = sectDict2Enum(r, [])
			origId, name = next(zip(*prepareNamesAndOrigIds(origIds)))
			yield KSEnumValue(name, value, origId, doc, None, None)


def parseAltnamelinesAppend(xprs):
	for el in xprs:
		v = el.value
		if ifAltnamelinesAppend(v.func):
			res = parseValueFromSourceEnumStr(correctedLiteralEval(v.args[0]).replace("\n", ""))
			if res:
				yield res


from icecream import ic


def parseFWrites(xprs):
	for el in xprs:
		v = el.value
		if ifFWrite(v.func):
			a = v.args[0]
			if isinstance(a, ast.BinOp):
				l = a.left
				if isinstance(l, ast.BinOp):
					lr = l.right
					if isinstance(lr, ast.Call) and ifStrLjust(lr.func):
						r = a.right
						name = correctedLiteralEval(lr.args[0])
						val = correctedLiteralEval(r).strip()
						if val[0] == "=" and val[-1] == ",":
							val = val[1:-1].strip()
							val = correctedLiteralEval(val)
							origId, name = next(zip(*prepareNamesAndOrigIds([name])))
							yield KSEnumValue(name, val, origId, None, None, None)


def parseMMPF(sourceAST):
	mmpfB = [el for el in sourceAST.body if isinstance(el, ast.FunctionDef) and el.name == "make_mapi_properties_file"][0].body
	xprs = [el for el in mmpfB if isinstance(el, ast.Expr) and isinstance(el.value, ast.Call)]
	yield from parsePropertiesAppend(xprs)
	yield from parseAltnamelinesAppend(xprs)
	yield from parseFWrites(xprs)


class OpenChangeSource(Source):
	__slots__ = ()

	def parseValuesFromSrc(self, src):
		src = py2to3(ast27.parse(src))
		for l in extractGroup1OfNames(src)["temporary_private_tags"].splitlines():
			if l:
				yield parseValueFromSourceEnumStr(l)
		yield from parseMMPF(src)


OpenChange = OpenChangeSource("OpenChange", "makepropslist.py", "https://raw.githubusercontent.com/zentyal/openchange/master/script/makepropslist.py", "GPL-3.0")
