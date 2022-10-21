from pathlib import Path

from PyQt6.QtWidgets import QApplication

from gui import JanelaPrincipal
from old_trabalhos import carrega_trabalhos_lista


def main():
    app = QApplication([])
    trabalhos = carrega_trabalhos_lista(Path("ordens/"))
    janela_principal = JanelaPrincipal(trabalhos)
    janela_principal.showMaximized()

    app.exec()


if __name__ == "__main__":
    main()
    print("Programa terminado.")
