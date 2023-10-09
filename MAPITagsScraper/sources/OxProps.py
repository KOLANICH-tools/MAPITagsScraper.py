import re
import xml.dom.minidom
from ast import literal_eval
from pathlib import Path
from xml.dom.minidom import Element

import commonmark
import docutils
import docutils.frontend
import recommonmark
from dom_query import select, select_all
from recommonmark.parser import CommonMarkParser

from ..DOMUtils import *
from ..KSEnumValue import KSEnumValue
from ..nameNormalizer import canonicalizeOrigName, convertName, prepareNamesAndOrigIds
from ..Source import Source, cachedFetchFile

__all__ = ("OxProps",)

oxprops_feed = "https://interoperability.blob.core.windows.net/files/MS-OXPROPS/%5bMS-OXPROPS%5d.rss"

companionValueDocRX = re.compile(r"Contains the (?:value of (?:the (?P<subject1>[^()\.]+?)(?:'s)?\s+)?|(?P<subject2>[^()\.]+?) of the )(?P<propName>Pid\w+) property \(section \d+(\.\d+)+\)(?:\.|, and)?")
propsInDocsRX = re.compile(r"(?P<propName>Pid\w+) property \((?:\[MS-\w+\] )?section \d+(\.\d+)+\)")


def filterPropsInDoc(doc: str):
	return propsInDocsRX.subn(lambda x: "`" + convertName(canonicalizeOrigName(x.group("propName"))) + "`", doc)[0]


def parseMarkdown(t: typing.Union[str, Path]) -> Element:
	if isinstance(t, Path):
		t = t.read_text(encoding="utf-8")
	s = docutils.frontend.OptionParser(components=(CommonMarkParser,)).get_default_values()
	p = CommonMarkParser()
	doc = docutils.utils.new_document(None, s)
	p.parse(t, doc)
	parsedDocs = doc.asdom()
	doc = next(iter(parsedDocs.childNodes))
	return doc


def pars2kvpairs(pars: typing.Iterable[Element]) -> typing.Iterable[typing.Tuple[str, str]]:
	"""Convert a list of `paragraph` tags into a tuple (key, value), where `key` is the content of `strong` tag, and `value` is the rest of `paragraph` content. In MS docs converted to MarkDown  in the sections we are interested in`strong` are headers and the rest of is contents"""
	for par in pars:
		nameNode = select(par, "strong")
		name = node2text(nameNode).strip()
		cont = textAfter(nameNode).strip()
		if name.endswith(":"):
			name = name[:-1]
		yield (name, cont)


def pars2map(pars: typing.Iterable[Element]) -> typing.Mapping[str, str]:
	"""Convert `paragraph` tags into a map"""
	return dict(pars2kvpairs(pars))


def getPidTagSections(md: Element) -> typing.Iterable[Element]:
	"""Gets Markdown sections that contain info about `PidTag`s"""

	for sec in select_all(md, "section[names][ids]"):
		if sec.attributes["ids"].value.startswith("pidtag"):
			yield sec


class SectionDict2Enum:
	__slots__ = ()

	DESCR_NAME = "Description"
	CAN_NAME = "Canonical name"
	PROP_ID_NAME = "Property ID"
	ALT_NAMES_NAME = "Alternate names"

	def __call__(self, smap, origIds):
		doc = smap.get(self.__class__.DESCR_NAME, None)
		cName = smap.get(self.__class__.CAN_NAME, None)
		if cName is not None:
			origIds.append(cName)
		valueSrc = smap.get(self.__class__.PROP_ID_NAME, None)
		altNames = smap.get(self.__class__.ALT_NAMES_NAME, None)
		if altNames:
			origIds.extend(el.strip() for el in altNames.split(","))

		return origIds, valueSrc, doc


sectDict2Enum = SectionDict2Enum()


def parseSectionIntoEnumItem(sec):
	name = node2text(select(sec, "title")).strip()
	return sectDict2Enum(pars2map(select_all(sec, "paragraph")), [name])


class DocxMarkdownSource(Source):
	__slots__ = ("cachedFileStem",)

	def __init__(self, name, cachedFileStem, uri, license):
		self.cachedFileStem = cachedFileStem
		super().__init__(name, cachedFileStem + ".md", uri, license)

	def fetch(self, cacheDir: Path) -> str:
		markdownCacheFile = cacheDir / self.cachedFileName

		if markdownCacheFile.is_file():
			return markdownCacheFile.read_text()

		data = convertDOCX2MarkDownMemory(getOxPropsDocx(cacheDir, self.cachedFileStem))
		markdownCacheFile.write_text(data)
		return data

	def parseValuesFromSrc(self, src):
		md = parseMarkdown(src)
		return [KSEnumValueFromSection(sec) for sec in getPidTagSections(md)]


def KSEnumValueFromSection(sec):
	origIds, valueSrc, doc = parseSectionIntoEnumItem(sec)
	origIds, names = prepareNamesAndOrigIds(origIds, True)
	value = literal_eval(valueSrc)

	companion = None
	subj = None
	if doc:
		compMatch = companionValueDocRX.match(doc)
		if compMatch:
			subj = compMatch.group("subject1")
			if not subj:
				subj = compMatch.group("subject2")
			subj = subj.strip()

			rawPropName = compMatch.group("propName").strip()
			convertedPropName = convertName(canonicalizeOrigName(rawPropName))

			s = compMatch.span()
			doc = doc[: s[0]] + doc[s[1] :]
			companion = convertedPropName

			if doc.startswith(", "):
				doc = doc[2:]

		doc = filterPropsInDoc(doc)

		if not doc:
			doc = None

	return KSEnumValue("_or_".join(names), value, origIds, doc, companion, subj)


def getOxPropsDocxLink():
	import httpx
	from bs4 import BeautifulSoup
	from dom_query import select

	r = httpx.get(oxprops_feed)
	d = xml.dom.minidom.parseString(r.text)

	i = select(d, "item")

	h = node2text(select(i, "description"))
	hd = BeautifulSoup(h, "lxml")
	for el in hd.select("a"):
		lh = el["href"]
		if lh.endswith(".docx"):
			return lh


def getOxPropsDocx(cacheDir: Path, cachedFileStem: str):
	return cachedFetchFile(cacheDir / (cachedFileStem + ".docx"), getOxPropsDocxLink())


targetMDFormat = "gfm+smart"
srcFmt = "docx"
extraPandocArgs = (
	"--from=docx",
	"--wrap=none",
)


def convertDOCX2MarkDownFile(inputFile: Path) -> str:
	import pypandoc

	return pypandoc.convert_file(str(inputFile), targetMDFormat, extra_args=extraPandocArgs)


def convertDOCX2MarkDownMemory(docx) -> str:
	import pypandoc

	return pypandoc.convert_text(docx, targetMDFormat, srcFmt, extra_args=extraPandocArgs)


oxprops = DocxMarkdownSource("oxprops", "[MS-OXPROPS]", oxprops_feed, "Microsoft proprietary, but reuse in other impls is explicitly allowed")
