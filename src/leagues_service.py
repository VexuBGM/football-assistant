from .services import leagues_service as _leagues_service
import sys

sys.modules[__name__] = _leagues_service
