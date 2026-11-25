"""Interfaces (abstractions) dont depend FileManager.

On respecte :
 - ISP : des petites interfaces, chacune avec un role precis
 - LSP : toute implementation doit pouvoir remplacer une autre (memes contrats)
 - DIP : FileManager depend de ces abstractions et pas de os/shutil/print/input
"""
from abc import ABC, abstractmethod


class FileSelection(ABC):
    """Fournit la liste des fichiers selectionnes"""

    @abstractmethod
    def get_selected_files(self):
        """Retourne la liste des chemins selectionnes"""

    @abstractmethod
    def clear_selection(self):
        """Vide la selection"""


class FileSystem(ABC):
    """Operations sur le systeme de fichiers utilisees par FileManager"""

    @abstractmethod
    def exists(self, path):
        pass

    @abstractmethod
    def is_file(self, path):
        pass

    @abstractmethod
    def is_dir(self, path):
        pass

    @abstractmethod
    def copy(self, source, destination):
        """Copie source vers destination, retourne le chemin cree"""

    @abstractmethod
    def move(self, source, destination):
        """Deplace source vers destination, retourne le nouveau chemin"""

    @abstractmethod
    def remove_file(self, path):
        pass

    @abstractmethod
    def remove_dir(self, path):
        pass


class UserInterface(ABC):
    """Ce que FileManager a besoin de l'interface utilisateur"""

    @abstractmethod
    def show_message(self, message):
        pass
