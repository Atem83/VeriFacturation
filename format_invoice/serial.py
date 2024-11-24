import polars as pl

class Serial:
    """Propriétés de la séquence de factures"""
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.prefix = kwargs.pop('prefix')
        self.suffix = kwargs.pop('suffix')
        self.start = kwargs.pop('start')
        self.end = kwargs.pop('end')
        self._invoices = self.emptyDF()
        self._missing = self.emptyDF()
        self._duplicate = self.emptyDF()

    def __repr__(self):
        return (f"{self.name}: (prefix: {self.prefix}, suffix: {self.suffix}, "
                + f"serial: {self.start}-{self.end})")

    @property
    def name(self):
        """Nom de la séquence de factures."""
        return self._name

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str):
            msg = "Le nom doit être une chaine de caractère"
            raise TypeError(msg)
        self._name = name

    @property
    def prefix(self):
        """Préfixe de la séquence de factures."""
        return self._prefix

    @prefix.setter
    def prefix(self, value: str | None):
        if not isinstance(value, str) and value is not None:
            msg = "Le préfixe doit être une chaine de caractère ou None"
            raise TypeError(msg)
        self._prefix = value

    @property
    def suffix(self):
        """Suffixe de la séquence de factures."""
        return self._suffix

    @suffix.setter
    def suffix(self, value: str | None):
        if not isinstance(value, str) and value is not None:
            msg = "Le suffixe doit être une chaine de caractère ou None"
            raise TypeError(msg)
        self._suffix = value

    @property
    def start(self):
        """Premier numéro de la séquence de factures."""
        return self._start

    @start.setter
    def start(self, value: int):
        if not isinstance(value, int) and value is not None:
            msg = "Le premier numéro doit être une valeur int ou None"
            raise TypeError(msg)
        self._start = value

    @property
    def end(self):
        """Dernier numéro de la séquence de factures."""
        return self._end

    @end.setter
    def end(self, value: int):
        if not isinstance(value, int) and value is not None:
            msg = "Le dernier numéro doit être une valeur int ou None"
            raise TypeError(msg)
        self._end = value

    @property
    def invoices(self):
        """Dataframe contenant les factures de la séquence."""
        return self._invoices
    
    @invoices.setter
    def invoices(self, value: pl.DataFrame):
        if not isinstance(value, pl.DataFrame):
            msg = "Le dataframe doit être un dataframe polars"
            raise TypeError(msg)
        self._invoices = value

    @property
    def missing(self):
        """Dataframe contenant les factures manquantes de la séquence."""
        return self._missing
    
    @missing.setter
    def missing(self, value: pl.DataFrame):
        if not isinstance(value, pl.DataFrame):
            msg = "Le dataframe doit être un dataframe polars"
            raise TypeError(msg)
        self._missing = value

    @property
    def duplicate(self):
        """Dataframe contenant les factures en doublon de la séquence."""
        return self._duplicate
    
    @duplicate.setter
    def duplicate(self, value: pl.DataFrame):
        if not isinstance(value, pl.DataFrame):
            msg = "Le dataframe doit être un dataframe polars"
            raise TypeError(msg)
        self._duplicate = value

    def emptyDF(self):
        df = pl.DataFrame({
            "PieceRef": pl.Series(dtype=pl.Utf8),
            "EcritureDate": pl.Series(dtype=pl.Date),
            "EcritureLib": pl.Series(dtype=pl.Utf8),
            "CompteNum": pl.Series(dtype=pl.Utf8),
            "Debit": pl.Series(dtype=pl.Float64),
            "Credit": pl.Series(dtype=pl.Float64)
        })
        return df

    def overlaps_with(self, other):
        """Vérifie si deux séquences de factures se chevauchent."""
        return self.start <= other.end and other.start <= self.end
