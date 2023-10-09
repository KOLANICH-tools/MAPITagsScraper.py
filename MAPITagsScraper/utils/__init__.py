import typing


def dedupPreservingOrder(args: typing.Iterable[str]) -> typing.Iterator[str]:
	dedup = set()
	for el in args:
		if el not in dedup:
			dedup.add(el)
			yield el


def sortedDictByKey(dic):
	return dic.__class__(sorted(dic.items(), key=lambda x: x[0]))
