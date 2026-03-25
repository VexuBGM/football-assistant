from .services import players_service as _players_service
import sys

sys.modules[__name__] = _players_service
