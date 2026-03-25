from .database import db as _db
import sys

sys.modules[__name__] = _db
