import os
import sys

import pystray
from PIL import Image
from pystray import Icon, MenuItem


def create_tray_icon():
    def quit_app(icon, item):
        icon.stop()
        os._exit(0)

    try:
        # Determina o caminho base dependendo do ambiente de execução
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Define o caminho do ícone
        icon_path = os.path.join(base_path, "static", "puzzle.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_path, "..", "static", "puzzle.ico")

        # Carrega a imagem do ícone
        image = Image.open(icon_path)
    except Exception as e:
        raise RuntimeError(
            f"O arquivo de ícone não foi encontrado. Caminho tentado: {icon_path}\nErro: {e}"
        )

    # Cria o menu do ícone da bandeja
    menu = pystray.Menu(MenuItem("Sair", quit_app))

    # Inicializa o ícone da bandeja
    tray_icon = Icon("QuestionnaireManager", image, "Questionnaire Manager", menu)
    tray_icon.run()
