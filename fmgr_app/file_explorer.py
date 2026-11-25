import os

from fmgr_app.interfaces import FileSelection


class FileSelector:
    def __init__(self):
        self.selected_files = []
        self.current_directory_contents = []

    def load_directory_contents(self, directory_path):
        """Load the contents of a directory"""
        try:
            self.current_directory_contents = os.listdir(directory_path)
            return self.current_directory_contents
        except Exception as e:
            print(f"Error loading directory contents: {e}")
            return []

    def select_files_by_indices(self, indices, directory_path):
        """Select files based on indices"""
        try:
            selected_indices = [int(i.strip()) for i in indices.split(',')]
            self.selected_files.clear()
            for index in selected_indices:
                if 0 <= index < len(self.current_directory_contents):
                    full_path = os.path.join(directory_path, self.current_directory_contents[index])
                    self.selected_files.append(full_path)

            print("Selected files:")
            for file in self.selected_files:
                print(f" - {os.path.basename(file)}")
            return self.selected_files
        except ValueError:
            print("Invalid input. Please enter valid indices.")
            return []

    def get_selected_files(self):
        """Return the list of currently selected files"""
        return self.selected_files

    def clear_selection(self):
        """Clear the current file selection"""
        self.selected_files.clear()


class FileExplorer(FileSelection):
    """Exploration des dossiers (affichage, navigation) + selection"""

    def __init__(self, start_path=None):
        self.current_path = start_path or os.path.expanduser('~')
        self.file_selector = FileSelector()

    def display_directory_contents(self):
        """Display contents of the current directory"""
        try:
            contents = self.file_selector.load_directory_contents(self.current_path)
            print(f"\nCurrent Directory: {self.current_path}")
            print("-" * 50)
            for index, element in enumerate(contents):
                full_path = os.path.join(self.current_path, element)
                element_type = "📁 Folder" if os.path.isdir(full_path) else "📄 File"
                print(f"{index}. {element_type}: {element}")
        except PermissionError:
            print("Access denied to this directory.")

    def navigate(self, index):
        """Navigate to a subdirectory"""
        try:
            contents = os.listdir(self.current_path)
            selected_element = contents[index]
            full_path = os.path.join(self.current_path, selected_element)
            if os.path.isdir(full_path):
                self.current_path = full_path
                self.display_directory_contents()
            else:
                print(f"Cannot open file {selected_element}")
        except (IndexError, OSError) as e:
            print(f"Navigation error: {e}")

    def go_to_parent_directory(self):
        """Move to the parent directory"""
        self.current_path = os.path.dirname(self.current_path)
        self.display_directory_contents()

    def select_files(self, indices):
        return self.file_selector.select_files_by_indices(indices, self.current_path)

    # --- implementation de FileSelection ---
    def get_selected_files(self):
        return self.file_selector.get_selected_files()

    def clear_selection(self):
        self.file_selector.clear_selection()
