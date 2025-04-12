import os
import time
import argparse
import hashlib
from watchdog.events import FileSystemEventHandler # type: ignore
from colorama import Fore, Style
from git_handler import git_commit_push
from git_observer.utils import get_current_directory
from watchdog.observers import Observer # type: ignore
import threading

# Définition des modes
MODE_AUTO = "auto"
MODE_PATTERN = "pattern"

# Liste des fichiers modifiés
MODIFIED_FILES = {}

class GitAutoCommitHandler(FileSystemEventHandler):
    """Surveille les fichiers et déclenche des commits automatiques ou sur modification."""
    
    
    def __init__(self, mode=MODE_AUTO, commit_delay=30, default_message="Mise à jour automatique"):
        super().__init__()
        self.mode = mode
        self.commit_delay = commit_delay
        self.default_message = default_message
        self.last_commit_time = time.time()


    def on_any_event(self, event):
        """Gère tous les événements (création, modification, suppression, déplacement)."""
        
        if event.is_directory or ".git" in event.src_path or os.path.basename(event.src_path).startswith("."):
            return

        event_type = event.event_type
        file_path = event.src_path

        if event_type in ["created", "modified", "moved"]:
            if self.is_file_modified(file_path):
                MODIFIED_FILES[file_path] = event_type
                print(f"{Fore.CYAN}📌 {event_type.upper()} : {file_path}{Style.RESET_ALL}")

        elif event_type == "deleted":
            MODIFIED_FILES[file_path] = "deleted"
            print(f"{Fore.RED}🗑️ SUPPRIMÉ : {file_path}{Style.RESET_ALL}")

        # Appliquer le mode choisi
        if self.mode == MODE_AUTO:
            self.try_commit()
        elif self.mode == MODE_PATTERN and event_type == "modified":
            self.commit_now()


    def is_file_modified(self, file_path):
        """Vérifie si un fichier a réellement changé en comparant son hash."""
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            previous_hash = MODIFIED_FILES.get(file_path, None)
            
            if file_hash != previous_hash:
                MODIFIED_FILES[file_path] = file_hash
                return True
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Erreur analyse fichier : {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️ Fichier non trouvé : {file_path}{Style.RESET_ALL}")
            return False


    def try_commit(self):
        """Vérifie s'il est temps de faire un commit groupé."""
        current_time = time.time()
        if (current_time - self.last_commit_time) > self.commit_delay and MODIFIED_FILES:
            self.commit_now()

    # def commit_now(self):
    #     """Effectue un commit immédiat avec les fichiers modifiés."""
    #     commit_message = self.default_message if self.default_message else self.generate_commit_message()
    #     git_commit_push(commit_message)
    #     MODIFIED_FILES.clear()
    #     self.last_commit_time = time.time()
    
    
    # def commit_now(self):
    #     """Effectue un commit immédiat avec confirmation."""
    #     if not MODIFIED_FILES:
    #         return

    #     print(f"{Fore.BLUE}📝 Fichiers à committer :")
    #     for file in MODIFIED_FILES:
    #         print(f"  - {file}")

    #     confirmation = input(f"{Fore.YELLOW}Confirmer le commit ? (o/N) {Style.RESET_ALL}").strip().lower()
    #     if confirmation != "o":
    #         print(f"{Fore.RED}🚫 Commit annulé.{Style.RESET_ALL}")
    #         return

    #     commit_message = self.default_message if self.default_message else self.generate_commit_message()
    #     git_commit_push(commit_message)
    #     MODIFIED_FILES.clear()
    #     self.last_commit_time = time.time()


    def commit_now(self):
        """Effectue un commit immédiat avec confirmation, avec un timeout de 2 minutes."""
        
        if not MODIFIED_FILES:
            return

        print(f"{Fore.BLUE}📝 Fichiers à committer :")
        for file in MODIFIED_FILES:
            print(f"  - {file}")

        # Fonction pour commit auto après timeout
        def auto_commit():
            print(f"\n{Fore.YELLOW}⏳ Temps écoulé. Commit automatique en cours...{Style.RESET_ALL}")
            self.execute_commit()

        # Démarrer un timer de 2 minutes (120 secondes)
        timer = threading.Timer(120, auto_commit)
        timer.start()

        try:
            confirmation = input(f"{Fore.YELLOW}Confirmer le commit ? (o/N) {Style.RESET_ALL}").strip().lower()
            timer.cancel()  # Annuler le timer si l'utilisateur répond avant les 2 minutes
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏳ Temps écoulé. Commit automatique en cours...{Style.RESET_ALL}")
            self.execute_commit()
            return

        if confirmation == "o":
            self.execute_commit()
        else:
            print(f"{Fore.RED}🚫 Commit annulé.{Style.RESET_ALL}")


    def execute_commit(self):
        """Exécute le commit et vide la liste des fichiers modifiés."""
        
        commit_message = self.default_message if self.default_message else self.generate_commit_message()
        
        git_commit_push(commit_message)
        MODIFIED_FILES.clear()
        self.last_commit_time = time.time()


    def generate_commit_message(self):
        """Génère un message de commit basé sur les modifications détectées."""
        
        created = [f for f, t in MODIFIED_FILES.items() if t == "created"]
        modified = [f for f, t in MODIFIED_FILES.items() if t == "modified"]
        deleted = [f for f, t in MODIFIED_FILES.items() if t == "deleted"]

        parts = []
        if created:
            parts.append(f"Ajouté : {', '.join(os.path.basename(f) for f in created)}{Style.RESET_ALL}")
        if modified:
            parts.append(f"Modifié : {', '.join(os.path.basename(f) for f in modified)}{Style.RESET_ALL}")
        if deleted:
            parts.append(f"Supprimé : {', '.join(os.path.basename(f) for f in deleted)}{Style.RESET_ALL}")

        return " | ".join(parts) if parts else "Mise à jour automatique"


def parse_arguments():
    """Analyse les arguments CLI pour configurer le comportement."""
    parser = argparse.ArgumentParser(description="Surveille un dossier et effectue des commits automatiques.")
    parser.add_argument("--mode", type=str, choices=[MODE_AUTO, MODE_PATTERN], default=MODE_AUTO, help="Mode d'exécution : 'auto' (par défaut) ou 'pattern'")
    parser.add_argument("--delay", type=int, default=30, help="Délai en secondes pour le commit automatique (mode auto).")
    parser.add_argument("--message", type=str, default="Mise à jour automatique", help="Message de commit par défaut.")

    return parser.parse_args()


# if __name__ == "__main__":
#     args = parse_arguments()
#     print(f"{Fore.GREEN}🚀 Mode : {args.mode}, Delay : {args.delay}s, Message : {args.message}{Style.RESET_ALL}")

#     event_handler = GitAutoCommitHandler(mode=args.mode, commit_delay=args.delay, default_message=args.message)


def start_watcher():
    """Démarre la surveillance du dossier"""
    
    args = parse_arguments()
    print(f"{Fore.GREEN}🚀 Mode : {args.mode}, Delay : {args.delay}s, Message : {args.message}{Style.RESET_ALL}")

    watched_dir = get_current_directory()
    print(f"{Fore.MAGENTA}👀 Surveillance du dossier : {watched_dir}{Style.RESET_ALL}")

    event_handler = GitAutoCommitHandler(mode=args.mode, commit_delay=args.delay, default_message=args.message)
    # event_handler = GitAutoCommitHandler()
    
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
    # Ajoute ici le code pour démarrer l'observation du dossier
