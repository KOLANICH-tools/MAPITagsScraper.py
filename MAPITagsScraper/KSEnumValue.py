import typing


class KSEnumValue:
	__slots__ = ("id", "value", "origIds", "doc", "companion", "subject")

	def __init__(self, iD: str, value: int, origIds: typing.Iterable[str], doc: str, companion: str = None, subject: str = None):
		self.id = iD
		self.value = value
		self.origIds = origIds
		self.doc = doc
		self.companion = companion
		self.subject = subject

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(getattr(self, k)) for k in self.__class__.__slots__) + ")"
