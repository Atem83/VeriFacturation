from .base_import import BaseImport
from .fec_import import FECImport
from .cador_import import CadorImport

import_classes = [CadorImport, FECImport]
import_names = [cls().name() for cls in import_classes]

__all__ = ["CadorImport", "FECImport", "import_names"]