from fmgr_app.interfaces import UserInterface


class ConsoleUI(UserInterface):
    """Interface utilisateur en mode console"""

    def show_message(self, message):
        print(message)

    def ask(self, question):
        return input(question)

    def error_choice(self, message):
        print(f"\n/!\\ {message}")
        print("0. Ignorer l'erreur et continuer")
        print("1. Toujours ignorer les erreurs")
        print("2. Stopper l'operation")
        print("3. Annuler l'operation (rollback)")
        while True:
            answer = input("Votre choix : ").strip()
            if answer in ("0", "1", "2", "3"):
                return int(answer)
            print("Choix invalide")
