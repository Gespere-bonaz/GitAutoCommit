import subprocess
import time
from colorama import Fore, Style
import threading
from datetime import datetime
from win10toast import ToastNotifier # type: ignore
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class CommitDialog:
    def __init__(self):
        self.result = None
        self.message = None
        
    def show(self):
        # Création de la fenêtre principale
        dialog = tk.Tk()
        dialog.title("Git Auto Commit")
        
        # Forcer la fenêtre au premier plan
        dialog.lift()
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        
        # Centrer la fenêtre
        window_width = 400
        window_height = 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        dialog.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Style
        dialog.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#f0f0f0')
        style.configure('Custom.TButton', padding=5, background='#e0e0e0', foreground='black')
        style.configure('Custom.TLabel', background='#f0f0f0', foreground='black')
        
        # Frame principal
        main_frame = ttk.Frame(dialog, style='Custom.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        ttk.Label(main_frame, 
                 text="Des modifications sont en attente depuis 30 minutes!", 
                 wraplength=350, 
                 justify="center",
                 style='Custom.TLabel').pack(pady=10)
        
        # Champ de saisie
        ttk.Label(main_frame, 
                 text="Message de commit:",
                 style='Custom.TLabel').pack(pady=5)
        message_entry = ttk.Entry(main_frame, width=40)
        message_entry.pack(pady=5)
        
        def on_ok():
            self.message = message_entry.get()
            self.result = True
            dialog.destroy()
            
        def on_cancel():
            self.result = False
            dialog.destroy()
        
        # Boutons
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(pady=20)
        
        commit_btn = tk.Button(button_frame, 
                             text="Commit", 
                             command=on_ok,
                             bg='#4CAF50',
                             fg='white',
                             padx=20,
                             pady=5)
        commit_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, 
                              text="Annuler",
                              command=on_cancel,
                              bg='#f44336',
                              fg='white',
                              padx=20,
                              pady=5)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        dialog.mainloop()
        return self.result, self.message

class GitHandler:
    """Gère les interactions avec Git"""
    
    def __init__(self):
        self.last_modification_time = None
        self.notification_thread = None
        # self.NOTIFICATION_DELAY = 1800  # 30 minutes
        self.NOTIFICATION_DELAY = 20  # Changez à 60 secondes pour tester
        self.toaster = ToastNotifier()

    @staticmethod
    def extract_commit_message(file_path):
        """Cherche une ligne contenant commit_name="message" et retourne le message."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "commit_name=" in line:
                        parts = line.split("commit_name=", 1)
                        if len(parts) > 1:
                            message = parts[1].strip().replace('"', '')
                            return message if message else None
        except Exception as e:
            
            print(f"{Fore.RED}❌ Erreur lors de la lecture du fichier : {e}{Style.RESET_ALL}")
        return None

    def check_notification_time(self):
        """Vérifie si 30 minutes se sont écoulées depuis la dernière modification"""
        while True:
            if self.last_modification_time:
                elapsed_time = time.time() - self.last_modification_time
                if elapsed_time >= self.NOTIFICATION_DELAY:
                    self.notify_user()
                    self.last_modification_time = None  # Réinitialise le timer
            time.sleep(60)  # Vérifie toutes les minutes

    def notify_user(self):
        """Notifie l'utilisateur avec une fenêtre modale et une notification système"""
        # Notification système Windows
        self.toaster.show_toast(
            "Git Auto Commit",
            "Des modifications sont en attente depuis 30 minutes !",
            duration=10,
            threaded=True
        )

        # Création d'un thread pour la fenêtre modale
        def show_dialog():
            root = tk.Tk()
            root.withdraw()  # Cache la fenêtre racine
            dialog = CommitDialog()
            result, message = dialog.show()
            
            if result and message:
                self.git_commit_push(message)
            else:
                print(f"{Fore.YELLOW}Les modifications restent en attente.{Style.RESET_ALL}")

        # Exécute la fenêtre modale dans le thread principal
        root = tk.Tk()
        root.withdraw()
        root.after(1000, show_dialog)  # Attend 1 seconde pour laisser la notification système s'afficher
        root.mainloop()

    def start_notification_thread(self):
        """Démarre le thread de notification"""
        self.notification_thread = threading.Thread(target=self.check_notification_time, daemon=True)
        self.notification_thread.start()

    def update_modification_time(self):
        """Met à jour le temps de la dernière modification"""
        self.last_modification_time = time.time()

    def git_commit_push(self, commit_message):
        """Ajoute, commit et pousse les modifications sur Git."""
        try:
            status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
            
            if not status_output:
                print(f"{Fore.YELLOW}⚠️ Aucun changement détecté, rien à commit.{Style.RESET_ALL}")
                return  

            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)

            print(f"{Fore.GREEN}✅ Commit et push réussi : {commit_message}{Style.RESET_ALL}")
            self.last_modification_time = None  # Réinitialise le timer après un commit réussi
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}❌ Erreur Git : {e}{Style.RESET_ALL}")
