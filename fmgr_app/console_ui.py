from fmgr_app.interfaces import UserInterface


class ConsoleUI(UserInterface):
    """Interface utilisateur en mode console"""

    def show_message(self, message):
        print(message)

    def ask(self, question):
        return input(question)
