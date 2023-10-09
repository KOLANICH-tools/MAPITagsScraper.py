import typing
from io import StringIO
from xml.dom.minidom import Element


def minidom2str(md: Element) -> str:
	with StringIO() as f:
		md.writexml(f, indent="\t", addindent="\t", newl="\n")
		return f.getvalue()


def minidom2bs4(md: Element) -> "bs4.BeautifulSoup":
	import bs4

	return bs4.BeautifulSoup(minidom2str(md), "lxml")


def getTextFromNodes(node: Element) -> typing.Iterable[str]:
	if node.nodeType == node.TEXT_NODE:
		yield node.data
	else:
		for cn in node.childNodes:
			yield from getTextFromNodes(cn)


def node2text(node: Element) -> str:
	return "".join(getTextFromNodes(node))


def iterNextSiblings(n: Element) -> typing.Iterable[Element]:
	while n.nextSibling:
		n = n.nextSibling
		yield n


def textAfter(n: Element) -> str:
	"""Get the text after the teg within the parent element untill its end"""
	return "".join(map(node2text, iterNextSiblings(n)))
