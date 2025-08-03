import logging
import os
import subprocess


def build_executable():
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.debug("Iniciando o processo de geração do executável...")
    try:
        subprocess.run(["pyinstaller", "--version"], check=True)
        logging.debug("PyInstaller está instalado.")
    except FileNotFoundError:
        logging.error(
            "PyInstaller não está instalado. Instale-o usando 'pip install pyinstaller'."
        )
        return

    main_script = "run.py"
    icon_path = os.path.join(os.getcwd(), "app", "static", "puzzle.ico")
    logging.debug("Configurando o comando do PyInstaller...")
    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--add-data",
        "app/templates;app/templates",
        "--add-data",
        "app/static;static",
        "--add-data",
        "config.py;.",
        "--add-data",
        "app/models.py;app",
        "--add-data",
        "app/auth/routes.py;app/auth",
        "--add-data",
        "app/main/routes.py;app/main",
        "--exclude-module",
        "psycopg2",
        "--exclude-module",
        "MySQLdb",
        "--exclude-module",
        "cx_Oracle",
        "--name",
        "QuestionnaireManager",
        "--icon",
        icon_path,
        "--clean",
        "--noconfirm",
        "--hidden-import",
        "pystray",
        "--hidden-import",
        "Pillow",
    ]
    command.append(main_script)
    try:
        subprocess.run(command, check=True)
        logging.info("Executável gerado com sucesso!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao gerar o executável: {e}")


if __name__ == "__main__":
    build_executable()
