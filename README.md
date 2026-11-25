# fmgr - Gestionnaire de fichiers console

Projet EPSI - Ateliers de test (testabilité, tests unitaires, couverture, mutation).

## Lancer

```bash
python3 fmgr.py
```

## Architecture (atelier 1)

- `fmgr_app/interfaces.py` : abstractions `FileSelection`, `FileSystem`, `UserInterface`
- `fmgr_app/file_explorer.py` : `FileExplorer` (exploration + selection)
- `fmgr_app/file_manager.py` : `FileManager` (copie / deplacement / suppression), dependances injectees par le constructeur
- `fmgr_app/os_file_system.py` : implementation `os` / `shutil` de `FileSystem`
- `fmgr_app/console_ui.py` : implementation console de `UserInterface`
