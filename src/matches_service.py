from .services import matches_service as _matches_service
import sys

sys.modules[__name__] = _matches_service
