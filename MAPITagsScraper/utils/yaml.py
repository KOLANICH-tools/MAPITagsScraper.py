from pathlib import Path


def dumpYaml(ksDocument, outFile: Path):
	from ruamel.yaml import YAML

	y = YAML(typ="rt")
	y.width = 100500
	y.indent(2, 4, 2)

	with outFile.open("wt", encoding="utf-8") as f:
		y.dump(ksDocument, f)
