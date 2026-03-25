from .services import clubs_service as _clubs_service
import sys

sys.modules[__name__] = _clubs_service
