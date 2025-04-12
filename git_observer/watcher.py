import time
import os
import subprocess
from watchdog.observers import Observer #type: ignore
from watchdog.events import FileSystemEventHandler #type: ignore
from colorama import Fore, Style
from .git_handler import GitHandler
from .utils import get_current_directory

class GitAutoCommitHandler(FileSystemEventHandler):
    """Classe qui écoute les modifications et pousse les commits automatiquement."""
    
    def __init__(self):
        super().__init__()
        self.git_handler = GitHandler()
        self.git_handler.start_notification_thread()  # Démarrage du thread de notification

    def on_modified(self, event):
        """Déclenché lorsqu'un fichier est modifié."""
        if event.is_directory or any(excluded in event.src_path for excluded in [".git", "node_modules"]) or os.path.basename(event.src_path).startswith("."):
            return  # Ignore les dossiers et fichiers cachés

        file_path = event.src_path
        print(f"{Fore.CYAN}🔄 Fichier modifié : {file_path}{Style.RESET_ALL}")

        # Met à jour le temps de la dernière modification
        self.git_handler.update_modification_time()

        commit_message = self.git_handler.extract_commit_message(file_path)
        if commit_message:
            self.git_handler.git_commit_push(commit_message)

def start_watcher():
    """Démarre la surveillance du dossier"""
    watched_dir = get_current_directory()
    print(f"{Fore.MAGENTA}👀 Surveillance du dossier : {watched_dir}{Style.RESET_ALL}")
    
    event_handler = GitAutoCommitHandler()
    observer = Observer()
    observer.schedule(event_handler, watched_dir, recursive=True)
    
    # Variables pour suivre l'état
    last_modification_time = 0
    last_status = None
    prompt_shown = False
    
    try:
        observer.start()
        while True:
            # Vérifie s'il y a des modifications
            status_output = subprocess.run(["git", "status", "--porcelain"], 
                                        capture_output=True, 
                                        text=True).stdout.strip()
            
            current_time = time.time()
            
            # Affiche le prompt uniquement si:
            # 1. Il y a des modifications
            # 2. Au moins 2 secondes se sont écoulées depuis la dernière modification
            # 3. Le prompt n'a pas déjà été affiché
            if (status_output and 
                current_time - last_modification_time > 2 and 
                not prompt_shown):
                print(f"\n{Fore.CYAN}💡 Vous pouvez entrer un message de commit : {Style.RESET_ALL}", end='', flush=True)
                message = input()
                if message and not message.startswith("[main"):
                    event_handler.git_handler.git_commit_push(message)
                prompt_shown = True
            
            # Met à jour les variables de suivi
            if status_output != last_status:
                last_status = status_output
                last_modification_time = current_time
                prompt_shown = False
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Arrêt de la surveillance...{Style.RESET_ALL}")
        observer.stop()
    observer.join()

def input_with_timeout():
    """Permet de recevoir une entrée utilisateur sans bloquer le programme"""
    import sys
    import select

    # Vérifie si des données sont disponibles sur stdin
    if sys.platform == 'win32':
        import msvcrt
        if msvcrt.kbhit():
            return input(f"{Fore.GREEN}✏️ Entrez votre message de commit : {Style.RESET_ALL}")
    else:
        # Pour Linux/Mac
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return input(f"{Fore.GREEN}✏️ Entrez votre message de commit : {Style.RESET_ALL}")
    return None
