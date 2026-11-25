""" File Manager Console Application
    Code de depart genere par IA (voir historique git), refactorise pour etre testable.
"""
from fmgr_app.console_ui import ConsoleUI
from fmgr_app.file_explorer import FileExplorer
from fmgr_app.file_manager import FileManager
from fmgr_app.os_file_system import OsFileSystem


def main_menu():
    ui = ConsoleUI()
    explorer = FileExplorer()
    # injection des dependances
    file_manager = FileManager(explorer, OsFileSystem(), ui)

    while True:
        print("\n--- File Explorer ---")
        print("1. Display Directory")
        print("2. Navigate")
        print("3. Go to Parent Directory")
        print("4. Select Files")
        print("5. Copy")
        print("6. Move")
        print("7. Delete")
        print("8. Quit")

        choice = ui.ask("Your choice: ")

        try:
            if choice == '1':
                explorer.display_directory_contents()
            elif choice == '2':
                index = int(ui.ask("Enter navigation index: "))
                explorer.navigate(index)
            elif choice == '3':
                explorer.go_to_parent_directory()
            elif choice == '4':
                explorer.display_directory_contents()
                indices = ui.ask("Enter file indices to select (comma-separated): ")
                explorer.select_files(indices)
            elif choice == '5':
                dest = ui.ask("Enter destination path for copying: ")
                file_manager.copy_files(dest)
            elif choice == '6':
                dest = ui.ask("Enter destination path for moving: ")
                file_manager.move_files(dest)
            elif choice == '7':
                file_manager.delete_files()
            elif choice == '8':
                print("Goodbye!")
                break
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid number")


if __name__ == "__main__":
    main_menu()
