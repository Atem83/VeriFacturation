from typing import List
from .serial import Serial

class SerialManager:
    """Permet de gérer les différentes séquences de numérotation."""
    def __init__(self, overlaps: bool = True):
        self._counter = 0 # Compteur pour générer des noms uniques
        self._serial_list = []
        self.overlaps = overlaps
    
    def __repr__(self):
        elements = [f"    {elem}," for elem in self.serial_list]
        return f"[\n{ '\n'.join(elements) }\n]"
    
    @property
    def serial_list(self):
        list: List[Serial] = self._serial_list
        return list
    
    def add_serial(self,
                   name: str | None = None, 
                   prefix: str | None = None,
                   suffix: str | None = None, 
                   start: int | None = None, 
                   end: int | None = None,
                   ):
        """Crée une nouvelle instance de Serial."""
        
        if name is None:
            self._counter += 1
            name = f"Série{self._counter}"
        
        self._serial_list.append(Serial(
            name=name, 
            prefix=prefix, 
            suffix=suffix, 
            start=start, 
            end=end
        ))
        
        self.check_overlaps()
        self._serial_list.sort(key=lambda x: (x.prefix or '', x.suffix or ''))

    def del_serial(self, name: str):
        """Supprime une instance de Serial."""
        for serial in self._serial_list:
            if serial.name == name:
                self._serial_list.remove(serial)

    @property
    def overlaps(self):
        """Exige des numérotations qui ne se chevauchent pas"""
        return self._overlaps
    
    @overlaps.setter
    def overlaps(self, boolean):
        if not isinstance(boolean, bool):
            msg = "Le format doit être un boolean"
            raise ValueError(msg)
        self._overlaps = boolean

    def list_overlaps(self):
        """Trouve toutes les séquences de numérotation qui se chevauchent."""
        
        # Groupe les instances Serial par (prefix, suffix)
        groups = {}
        for serial in self.serial_list:
            key = (serial.prefix, serial.suffix)
            groups.setdefault(key, []).append(serial)
        
        overlap_results = []

        # S'il y a moins de deux instances Serial, renvoyer une liste vide
        if sum(len(valeur) for valeur in groups.values()) < 2:
            return overlap_results

        # Liste les séquences de numérotation qui se chevauchent
        for (prefix, suffix), items in groups.items():
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    if items[i].overlaps_with(items[j]):
                        overlap_results.append({
                            "prefix": prefix,
                            "suffix": suffix,
                            "overlap_between": (items[i], items[j])
                        })
        
        return overlap_results

    def check_overlaps(self):
        """Verifie si les numérotations ne se chevauchent pas"""
        if self.overlaps and len(self.list_overlaps()) > 0:
            msg = ("Les valeurs 'start' et 'end' des paires prefix-suffix " +
                   "identiques ne doivent pas se chevaucher")
            raise ValueError(msg)