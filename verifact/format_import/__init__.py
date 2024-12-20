from .base_import import BaseImport
from .fec_import import FECImport
from .cador_xlsx_import import CadorXlsxImport
from .cador_csv_import import CadorCsvImport

import_classes = [CadorCsvImport, CadorXlsxImport, FECImport]
import_names = [cls().name() for cls in import_classes]

__all__ = ["CadorCsvImport", "CadorXlsxImport", "FECImport", "import_names"]