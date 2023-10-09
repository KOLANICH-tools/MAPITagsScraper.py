from .genTagArray import genTagArray
from .kaitai import _kaitai
from .mfmy_mfoy import mfmy, mfoy
from .OxProps import oxprops
from .ptags import ptags
from .openchange import OpenChange

sources = (oxprops, mfmy, mfoy, genTagArray, ptags, OpenChange)

sources = {s.name: s for s in sources}
