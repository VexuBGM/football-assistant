from .services import transfers_service as _transfers_service
import sys

sys.modules[__name__] = _transfers_service
