from .services import standings_service as _standings_service
import sys

sys.modules[__name__] = _standings_service
