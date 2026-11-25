class FileManager:
    """Traitements sur les fichiers selectionnes (copie, deplacement, suppression).

    Toutes les dependances sont injectees par le constructeur :
     - selection : FileSelection (qui donne les fichiers a traiter)
     - file_system : FileSystem (acces disque)
     - ui : UserInterface (messages a l'utilisateur)
    """

    def __init__(self, selection, file_system, ui):
        self.selection = selection
        self.fs = file_system
        self.ui = ui

    def copy_files(self, destination):
        """Copy selected files"""
        try:
            selected_files = self.selection.get_selected_files()
            for file in selected_files:
                if self.fs.exists(file):
                    self.fs.copy(file, destination)
            self.ui.show_message(f"{len(selected_files)} file(s) copied")
            self.selection.clear_selection()
        except Exception as e:
            self.ui.show_message(f"Copy error: {e}")

    def move_files(self, destination):
        """Move selected files"""
        try:
            selected_files = self.selection.get_selected_files()
            for file in selected_files:
                if self.fs.exists(file):
                    self.fs.move(file, destination)
            self.ui.show_message(f"{len(selected_files)} file(s) moved")
            self.selection.clear_selection()
        except Exception as e:
            self.ui.show_message(f"Move error: {e}")

    def delete_files(self):
        """Delete selected files"""
        try:
            selected_files = self.selection.get_selected_files()
            for file in selected_files:
                if self.fs.is_file(file):
                    self.fs.remove_file(file)
                elif self.fs.is_dir(file):
                    self.fs.remove_dir(file)
            self.ui.show_message(f"{len(selected_files)} file(s)/folder(s) deleted")
            self.selection.clear_selection()
        except Exception as e:
            self.ui.show_message(f"Delete error: {e}")
