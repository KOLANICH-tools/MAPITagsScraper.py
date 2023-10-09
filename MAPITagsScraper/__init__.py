#!/usr/bin/env python3

import re
import typing
from ast import literal_eval
from copy import deepcopy
from io import StringIO
from pathlib import Path
from warnings import warn

from .KSEnumValue import KSEnumValue
from .nameNormalizer import *
from .sources.kaitai import _kaitai
from .utils import dedupPreservingOrder
from .sources.kaitai import SerializingContext


__all__ = ("fullPipeline",)

def getTagsWithNonUniqueNames():
	return [(el.id, el.origIds) for el in parsed if "_or_" in el.id]


def normalizeUniqueNames(t):
	from .nameNormalizer import convertName

	for k in list(t.keys()):
		if not isinstance(t[k], str):
			if t[k]["id"] == "unkn":
				oids = list(dedupPreservingOrder(t[k]["-orig-id"]))
				if len(oids) == 1:
					v = list(oids)[0]
					fv = convertName(v)
					t[k]["id"] = fv
					t[k]["-orig-id"] = v


def mergeSourceIntoContext(ctx: SerializingContext, s: Source.Source, cacheDir: Path) -> None:
	tagsFromSource = s.parseEnumValues(cacheDir)
	ctx.enumValues2KSEnumDict(tagsFromSource)
	ctx.insertSource(s.uri, s.license)


def fullPipeline(outputDir: Path, sourcesList: typing.Iterable[Source.Source], cacheDir: Path) -> None:
	ctx = _kaitai._getCtxFromDir(outputDir)

	for s in sourcesList:
		mergeSourceIntoContext(ctx, s, cacheDir)

	ctx.sortByKey()
	ctx.dump(outputDir)
