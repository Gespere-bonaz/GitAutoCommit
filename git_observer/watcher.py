import time
import os
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore
from colorama import Fore, Style
from .git_handler import GitHandler
from .utils import get_current_directory

#Gespere test 

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

    try:
        observer.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Arrêt de la surveillance...{Style.RESET_ALL}")
        observer.stop()
    observer.join()
