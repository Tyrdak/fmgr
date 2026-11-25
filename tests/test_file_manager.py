"""Tests unitaires de FileManager : les 3 dependances sont simulees avec des mocks"""
from unittest.mock import MagicMock, call

import pytest

from fmgr_app.file_manager import FileManager
from fmgr_app.interfaces import (ALWAYS_IGNORE, CANCEL, IGNORE, STOP,
                                 FileSelection, FileSystem, UserInterface)

DEST = "/dest"


@pytest.fixture
def selection():
    sel = MagicMock(spec=FileSelection)
    sel.get_selected_files.return_value = []
    return sel


@pytest.fixture
def fs():
    fake = MagicMock(spec=FileSystem)
    fake.exists.return_value = True
    fake.is_file.return_value = True
    fake.is_dir.return_value = False
    # copy / move retournent le chemin cree dans la destination
    fake.copy.side_effect = lambda src, dst: f"{dst}/{src.split('/')[-1]}"
    fake.move.side_effect = lambda src, dst: f"{dst}/{src.split('/')[-1]}"
    return fake


@pytest.fixture
def ui():
    return MagicMock(spec=UserInterface)


@pytest.fixture
def manager(selection, fs, ui):
    return FileManager(selection, fs, ui)


def select(selection, *files):
    selection.get_selected_files.return_value = list(files)


def fail_on(*bad_files, error=OSError("boom")):
    """side_effect qui leve une erreur pour certains fichiers seulement"""
    def side_effect(src, dst=None):
        if src in bad_files:
            raise error
        return f"{dst}/{src.split('/')[-1]}" if dst else None
    return side_effect


# ---------------------------------------------------------------- copy_files

class TestCopyFiles:
    def test_copie_un_fichier(self, manager, selection, fs, ui):
        select(selection, "/a.txt")
        manager.copy_files(DEST)
        fs.copy.assert_called_once_with("/a.txt", DEST)
        ui.show_message.assert_called_once_with("1 file(s) copied")
        selection.clear_selection.assert_called_once()
        ui.error_choice.assert_not_called()

    def test_copie_plusieurs_fichiers_dans_l_ordre(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        manager.copy_files(DEST)
        assert fs.copy.call_args_list == [call("/a", DEST), call("/b", DEST), call("/c", DEST)]
        ui.show_message.assert_called_once_with("3 file(s) copied")

    def test_selection_vide(self, manager, selection, fs, ui):
        manager.copy_files(DEST)
        fs.copy.assert_not_called()
        ui.show_message.assert_called_once_with("0 file(s) copied")
        selection.clear_selection.assert_called_once()

    def test_selection_none(self, manager, selection, fs, ui):
        selection.get_selected_files.return_value = None
        manager.copy_files(DEST)
        fs.copy.assert_not_called()
        ui.show_message.assert_called_once_with("0 file(s) copied")

    def test_destination_vide_refusee(self, manager, selection, fs, ui):
        select(selection, "/a")
        manager.copy_files("")
        fs.copy.assert_not_called()
        ui.show_message.assert_called_once_with("Copy error: no destination")

    def test_destination_espaces_refusee(self, manager, selection, fs, ui):
        select(selection, "/a")
        manager.copy_files("   ")
        fs.copy.assert_not_called()
        ui.show_message.assert_called_once_with("Copy error: no destination")

    def test_beaucoup_de_fichiers(self, manager, selection, fs, ui):
        files = [f"/f{i}" for i in range(1000)]
        select(selection, *files)
        manager.copy_files(DEST)
        assert fs.copy.call_count == 1000
        ui.show_message.assert_called_once_with("1000 file(s) copied")

    def test_fichier_inexistant_demande_choix(self, manager, selection, fs, ui):
        select(selection, "/a", "/absent", "/b")
        fs.exists.side_effect = lambda p: p != "/absent"
        ui.error_choice.return_value = IGNORE
        manager.copy_files(DEST)
        ui.error_choice.assert_called_once()
        assert "/absent" in ui.error_choice.call_args[0][0]
        assert fs.copy.call_args_list == [call("/a", DEST), call("/b", DEST)]
        ui.show_message.assert_called_once_with("2 file(s) copied")

    def test_erreur_io_ignorer(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.copy.side_effect = fail_on("/b")
        ui.error_choice.return_value = IGNORE
        manager.copy_files(DEST)
        assert fs.copy.call_count == 3
        ui.show_message.assert_called_once_with("2 file(s) copied")

    def test_message_d_erreur_contient_operation_et_cause(self, manager, selection, fs, ui):
        select(selection, "/b")
        fs.copy.side_effect = fail_on("/b", error=PermissionError("locked"))
        ui.error_choice.return_value = STOP
        manager.copy_files(DEST)
        ui.error_choice.assert_called_once_with("Copy error on /b: locked")

    def test_toujours_ignorer_ne_redemande_pas(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c", "/d")
        fs.copy.side_effect = fail_on("/a", "/b", "/c")
        ui.error_choice.return_value = ALWAYS_IGNORE
        manager.copy_files(DEST)
        ui.error_choice.assert_called_once()
        assert fs.copy.call_count == 4
        ui.show_message.assert_called_once_with("1 file(s) copied")

    def test_ignorer_redemande_a_chaque_erreur(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.copy.side_effect = fail_on("/a", "/b")
        ui.error_choice.return_value = IGNORE
        manager.copy_files(DEST)
        assert ui.error_choice.call_count == 2

    def test_stop_arrete_l_operation(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.copy.side_effect = fail_on("/b")
        ui.error_choice.return_value = STOP
        manager.copy_files(DEST)
        assert fs.copy.call_args_list == [call("/a", DEST), call("/b", DEST)]
        fs.remove_file.assert_not_called()
        ui.show_message.assert_called_once_with("1 file(s) copied")
        selection.clear_selection.assert_called_once()

    def test_choix_inconnu_se_comporte_comme_stop(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.copy.side_effect = fail_on("/b")
        ui.error_choice.return_value = 42
        manager.copy_files(DEST)
        assert fs.copy.call_count == 2
        ui.show_message.assert_called_once_with("1 file(s) copied")

    def test_annuler_supprime_les_copies(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.copy.side_effect = fail_on("/c")
        ui.error_choice.return_value = CANCEL
        manager.copy_files(DEST)
        # rollback dans l'ordre inverse
        assert fs.remove_file.call_args_list == [call("/dest/b"), call("/dest/a")]
        ui.show_message.assert_called_once_with("0 file(s) copied")
        selection.clear_selection.assert_called_once()

    def test_annuler_supprime_un_dossier_copie(self, manager, selection, fs, ui):
        select(selection, "/dir", "/x")
        fs.copy.side_effect = fail_on("/x")
        fs.is_dir.side_effect = lambda p: p == "/dest/dir"
        ui.error_choice.return_value = CANCEL
        manager.copy_files(DEST)
        fs.remove_dir.assert_called_once_with("/dest/dir")
        fs.remove_file.assert_not_called()

    def test_annuler_sur_premier_fichier(self, manager, selection, fs, ui):
        select(selection, "/a", "/b")
        fs.copy.side_effect = fail_on("/a")
        ui.error_choice.return_value = CANCEL
        manager.copy_files(DEST)
        fs.remove_file.assert_not_called()
        assert fs.copy.call_count == 1
        ui.show_message.assert_called_once_with("0 file(s) copied")

    def test_erreur_pendant_rollback(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.copy.side_effect = fail_on("/c")
        fs.remove_file.side_effect = fail_on("/dest/b", error=OSError("busy"))
        ui.error_choice.return_value = CANCEL
        manager.copy_files(DEST)
        # /dest/a est quand meme supprime
        assert fs.remove_file.call_args_list == [call("/dest/b"), call("/dest/a")]
        assert ui.show_message.call_args_list == [
            call("Rollback error: busy"),
            call("1 file(s) copied"),
        ]

    def test_erreur_selection_ne_plante_pas(self, manager, selection, fs, ui):
        selection.get_selected_files.side_effect = RuntimeError("oups")
        manager.copy_files(DEST)
        ui.show_message.assert_called_once_with("Copy error: oups")
        fs.copy.assert_not_called()


    def test_rollback_appelle_chaque_undo_une_seule_fois(self, manager, ui):
        undos = [MagicMock(name="undo_a"), MagicMock(name="undo_b")]
        stack = list(undos)
        restant = manager._rollback(stack, 2)
        undos[0].assert_called_once_with()
        undos[1].assert_called_once_with()
        assert restant == 0
        assert stack == []
        ui.show_message.assert_not_called()


# ---------------------------------------------------------------- move_files

class TestMoveFiles:
    def test_deplace_un_fichier(self, manager, selection, fs, ui):
        select(selection, "/a.txt")
        manager.move_files(DEST)
        fs.move.assert_called_once_with("/a.txt", DEST)
        ui.show_message.assert_called_once_with("1 file(s) moved")
        selection.clear_selection.assert_called_once()

    def test_deplace_plusieurs(self, manager, selection, fs, ui):
        select(selection, "/a", "/b")
        manager.move_files(DEST)
        assert fs.move.call_args_list == [call("/a", DEST), call("/b", DEST)]
        ui.show_message.assert_called_once_with("2 file(s) moved")

    def test_selection_vide(self, manager, selection, fs, ui):
        manager.move_files(DEST)
        fs.move.assert_not_called()
        ui.show_message.assert_called_once_with("0 file(s) moved")
        selection.clear_selection.assert_called_once()

    def test_destination_vide_refusee(self, manager, selection, fs, ui):
        select(selection, "/a")
        manager.move_files("")
        fs.move.assert_not_called()
        ui.show_message.assert_called_once_with("Move error: no destination")

    def test_destination_none_refusee(self, manager, selection, fs, ui):
        select(selection, "/a")
        manager.move_files(None)
        fs.move.assert_not_called()
        ui.show_message.assert_called_once_with("Move error: no destination")

    def test_fichier_inexistant(self, manager, selection, fs, ui):
        select(selection, "/absent")
        fs.exists.return_value = False
        ui.error_choice.return_value = IGNORE
        manager.move_files(DEST)
        fs.move.assert_not_called()
        ui.error_choice.assert_called_once_with(
            "Move error on /absent: /absent does not exist")
        ui.show_message.assert_called_once_with("0 file(s) moved")

    def test_toujours_ignorer(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.move.side_effect = fail_on("/a", "/c")
        ui.error_choice.return_value = ALWAYS_IGNORE
        manager.move_files(DEST)
        ui.error_choice.assert_called_once()
        ui.show_message.assert_called_once_with("1 file(s) moved")

    def test_stop(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.move.side_effect = fail_on("/b")
        ui.error_choice.return_value = STOP
        manager.move_files(DEST)
        assert fs.move.call_count == 2
        ui.show_message.assert_called_once_with("1 file(s) moved")

    def test_annuler_remet_les_fichiers_en_place(self, manager, selection, fs, ui):
        select(selection, "/src/a", "/src/b", "/src/c")
        fs.move.side_effect = fail_on("/src/c")
        ui.error_choice.return_value = CANCEL
        manager.move_files(DEST)
        assert fs.move.call_args_list == [
            call("/src/a", DEST), call("/src/b", DEST), call("/src/c", DEST),
            call("/dest/b", "/src/b"), call("/dest/a", "/src/a"),
        ]
        ui.show_message.assert_called_once_with("0 file(s) moved")


# ---------------------------------------------------------------- delete_files

class TestDeleteFiles:
    def test_supprime_un_fichier(self, manager, selection, fs, ui):
        select(selection, "/a.txt")
        manager.delete_files()
        fs.remove_file.assert_called_once_with("/a.txt")
        fs.remove_dir.assert_not_called()
        ui.show_message.assert_called_once_with("1 file(s)/folder(s) deleted")
        selection.clear_selection.assert_called_once()

    def test_supprime_un_dossier(self, manager, selection, fs, ui):
        select(selection, "/dir")
        fs.is_file.return_value = False
        fs.is_dir.return_value = True
        manager.delete_files()
        fs.remove_dir.assert_called_once_with("/dir")
        fs.remove_file.assert_not_called()
        ui.show_message.assert_called_once_with("1 file(s)/folder(s) deleted")

    def test_fichiers_et_dossiers_melanges(self, manager, selection, fs, ui):
        select(selection, "/a", "/dir", "/b")
        fs.is_file.side_effect = lambda p: p != "/dir"
        fs.is_dir.side_effect = lambda p: p == "/dir"
        manager.delete_files()
        assert fs.remove_file.call_args_list == [call("/a"), call("/b")]
        fs.remove_dir.assert_called_once_with("/dir")
        ui.show_message.assert_called_once_with("3 file(s)/folder(s) deleted")

    def test_selection_vide(self, manager, selection, fs, ui):
        manager.delete_files()
        fs.remove_file.assert_not_called()
        ui.show_message.assert_called_once_with("0 file(s)/folder(s) deleted")
        selection.clear_selection.assert_called_once()

    def test_fichier_inexistant(self, manager, selection, fs, ui):
        select(selection, "/absent", "/a")
        fs.is_file.side_effect = lambda p: p == "/a"
        fs.is_dir.return_value = False
        ui.error_choice.return_value = IGNORE
        manager.delete_files()
        ui.error_choice.assert_called_once_with(
            "Delete error on /absent: /absent does not exist")
        fs.remove_file.assert_called_once_with("/a")
        ui.show_message.assert_called_once_with("1 file(s)/folder(s) deleted")

    def test_fichier_verrouille_stop(self, manager, selection, fs, ui):
        select(selection, "/a", "/locked", "/b")
        fs.remove_file.side_effect = fail_on("/locked", error=PermissionError("locked"))
        ui.error_choice.return_value = STOP
        manager.delete_files()
        assert fs.remove_file.call_args_list == [call("/a"), call("/locked")]
        ui.show_message.assert_called_once_with("1 file(s)/folder(s) deleted")

    def test_toujours_ignorer(self, manager, selection, fs, ui):
        select(selection, "/a", "/b", "/c")
        fs.remove_file.side_effect = fail_on("/a", "/b")
        ui.error_choice.return_value = ALWAYS_IGNORE
        manager.delete_files()
        ui.error_choice.assert_called_once()
        assert fs.remove_file.call_count == 3
        ui.show_message.assert_called_once_with("1 file(s)/folder(s) deleted")

    def test_annuler_impossible_previent_utilisateur(self, manager, selection, fs, ui):
        select(selection, "/a", "/b")
        fs.remove_file.side_effect = fail_on("/b")
        ui.error_choice.return_value = CANCEL
        manager.delete_files()
        assert ui.show_message.call_args_list == [
            call("Rollback impossible for some operations (delete)"),
            call("1 file(s)/folder(s) deleted"),
        ]

    def test_annuler_sans_rien_supprime(self, manager, selection, fs, ui):
        select(selection, "/a")
        fs.remove_file.side_effect = fail_on("/a")
        ui.error_choice.return_value = CANCEL
        manager.delete_files()
        ui.show_message.assert_called_once_with("0 file(s)/folder(s) deleted")
