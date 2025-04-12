import os
import subprocess
import platform
from colorama import init

# 🖌️ Initialisation de Colorama pour Windows
init(autoreset=True)

def get_current_directory():
    """Récupération du dossier courant (compatible Linux & Windows)"""
    return os.getcwd() if platform.system() == "Windows" else subprocess.run(["pwd"], capture_output=True, text=True).stdout.strip()
