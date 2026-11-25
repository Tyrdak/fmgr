from fmgr_app.interfaces import ALWAYS_IGNORE, CANCEL, IGNORE


class FileManager:
    """Traitements sur les fichiers selectionnes (copie, deplacement, suppression).

    Toutes les dependances sont injectees par le constructeur :
     - selection : FileSelection (qui donne les fichiers a traiter)
     - file_system : FileSystem (acces disque)
     - ui : UserInterface (messages et choix en cas d'erreur)
    """

    def __init__(self, selection, file_system, ui):
        self.selection = selection
        self.fs = file_system
        self.ui = ui

    def copy_files(self, destination):
        """Copy selected files"""
        def copy(file):
            if not self.fs.exists(file):
                raise FileNotFoundError(f"{file} does not exist")
            created = self.fs.copy(file, destination)
            return lambda: self._remove(created)

        count = self._process("Copy", copy)
        self.ui.show_message(f"{count} file(s) copied")

    def move_files(self, destination):
        """Move selected files"""
        def move(file):
            if not self.fs.exists(file):
                raise FileNotFoundError(f"{file} does not exist")
            new_path = self.fs.move(file, destination)
            return lambda: self.fs.move(new_path, file)

        count = self._process("Move", move)
        self.ui.show_message(f"{count} file(s) moved")

    def delete_files(self):
        """Delete selected files"""
        def delete(file):
            if self.fs.is_file(file):
                self.fs.remove_file(file)
            elif self.fs.is_dir(file):
                self.fs.remove_dir(file)
            else:
                raise FileNotFoundError(f"{file} does not exist")
            return None  # pas de rollback possible pour une suppression

        count = self._process("Delete", delete)
        self.ui.show_message(f"{count} file(s)/folder(s) deleted")

    def _remove(self, path):
        if self.fs.is_dir(path):
            self.fs.remove_dir(path)
        else:
            self.fs.remove_file(path)

    def _process(self, operation, action):
        """Applique action sur chaque fichier selectionne en gerant les erreurs.

        action(file) fait le traitement et retourne une fonction d'annulation (ou None).
        Retourne le nombre de fichiers traites.
        """
        files = list(self.selection.get_selected_files())
        undo_stack = []
        count = 0
        always_ignore = False

        for file in files:
            try:
                undo = action(file)
            except Exception as e:
                if always_ignore:
                    continue
                choice = self.ui.error_choice(f"{operation} error on {file}: {e}")
                if choice == IGNORE:
                    continue
                if choice == ALWAYS_IGNORE:
                    always_ignore = True
                    continue
                if choice == CANCEL:
                    count = self._rollback(undo_stack, count)
                # STOP (ou choix inconnu) : on arrete
                break
            count += 1
            if undo is not None:
                undo_stack.append(undo)

        self.selection.clear_selection()
        return count

    def _rollback(self, undo_stack, count):
        """Annule les operations deja faites (dans l'ordre inverse)"""
        if count > len(undo_stack):
            self.ui.show_message("Rollback impossible for some operations (delete)")
        while undo_stack:
            undo = undo_stack.pop()
            try:
                undo()
                count -= 1
            except Exception as e:
                self.ui.show_message(f"Rollback error: {e}")
        return count
