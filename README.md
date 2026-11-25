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

## Gestion des erreurs (atelier 1 - etape 3)

Quand une operation echoue sur un fichier (fichier inexistant, erreur E/S, fichier verrouille...),
`FileManager` appelle `UserInterface.error_choice(message)` qui retourne :

| Choix | Effet |
|-------|-------|
| 0 | Ignorer l'erreur et continuer |
| 1 | Toujours ignorer les erreurs (on ne redemande plus) |
| 2 | Stopper l'operation en cours |
| 3 | Annuler l'operation et rollback des fichiers deja traites |

Le rollback marche pour la copie (on supprime les copies) et le deplacement (on remet les fichiers a leur place).
Pour la suppression on ne peut pas revenir en arriere, un message previent l'utilisateur.

## Tests (atelier 2)

Installation :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Lancer les tests :

```bash
pytest
```

### Couverture de code (lignes + branches)

```bash
pytest --cov=fmgr_app.file_manager --cov-branch --cov-report=term-missing --cov-report=html
```

Le rapport HTML est dans `htmlcov/index.html`. On cible `FileManager` (la classe testee unitairement).
Resultat : 100% des lignes et 100% des branches (if/else) couvertes.
