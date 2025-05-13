import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
import subprocess
import json
import os
from PIL import Image, ImageTk
import customtkinter as ctk
import win32gui
import win32con
import win32api
import win32ui
from PIL import Image, ImageDraw
import time
import psutil
import threading
from datetime import datetime, timedelta

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Chemin du fichier de sauvegarde
SAVE_FILE = "games.json"

# Variable globale pour suivre les processus en cours
running_processes = {}
should_monitor = True

def format_playtime(seconds):
    """Convertit les secondes en format lisible"""
    if seconds < 3600:  # Moins d'une heure
        return f"{int(seconds // 60)} min"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}min"

def monitor_process(pid, game_index):
    """Surveille un processus de jeu et met à jour son temps de jeu"""
    start_time = time.time()
    try:
        process = psutil.Process(pid)
        while process.is_running() and should_monitor:
            time.sleep(1)
            games[game_index]["playtime"] = games[game_index].get("playtime", 0) + 1
            save_games()
            refresh_buttons()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    finally:
        if pid in running_processes:
            del running_processes[pid]

def get_file_icon(file_path, size=(32, 32)):
    try:
        large, small = win32gui.ExtractIconEx(file_path, 0)
        if large:
            win32gui.DestroyIcon(small[0])
            
            # Créer un DC et un bitmap pour l'icône
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, size[0], size[1])
            hdc = hdc.CreateCompatibleDC()
            
            # Sélectionner le bitmap
            hdc.SelectObject(hbmp)
            
            # Dessiner l'icône
            win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, large[0], 
                              size[0], size[1], 0, None, win32con.DI_NORMAL)
            
            # Convertir le bitmap en PIL Image
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGBA',
                size,
                bmpstr, 'raw', 'BGRA', 0, 1
            )
            
            win32gui.DestroyIcon(large[0])
            
            return ImageTk.PhotoImage(img)
    except:
        # Créer une icône par défaut
        img = Image.new('RGBA', size, (45, 45, 45, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([2, 2, size[0]-3, size[1]-3], outline=(100, 100, 100, 255))
        return ImageTk.PhotoImage(img)

# Charger les jeux depuis un fichier
def load_games():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return []

# Sauvegarder les jeux
def save_games():
    with open(SAVE_FILE, "w") as f:
        json.dump(games, f)

# Lancer le jeu
def launch_game(path, game_index):
    process = subprocess.Popen(path, shell=True)
    pid = process.pid
    running_processes[pid] = process
    
    # Démarrer le monitoring dans un thread séparé
    monitor_thread = threading.Thread(target=monitor_process, args=(pid, game_index))
    monitor_thread.daemon = True
    monitor_thread.start()

# Ajouter un nouveau jeu
def add_game():
    path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
    if path:
        name = simpledialog.askstring("Nom du jeu", "Entre le nom du jeu :")
        if name:
            games.append({"name": name, "path": path, "playtime": 0})
            save_games()
            refresh_buttons()

# Supprimer un jeu
def delete_game(index):
    if 0 <= index < len(games):
        games.pop(index)
        save_games()
        refresh_buttons()

# Rafraîchir les boutons
def refresh_buttons():
    for widget in frame.winfo_children():
        widget.destroy()
    
    for i, game in enumerate(games):
        game_frame = ctk.CTkFrame(frame)
        game_frame.pack(fill="x", pady=5, padx=5)
        
        # Obtenir l'icône du jeu
        icon = get_file_icon(game["path"])
        
        # Label pour l'icône
        icon_label = tk.Label(game_frame, image=icon, bg="#2B2B2B")
        icon_label.image = icon  # Garder une référence
        icon_label.pack(side="left", padx=5)
        
        # Frame pour le nom et le temps de jeu
        info_frame = ctk.CTkFrame(game_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Nom du jeu
        name_label = ctk.CTkLabel(
            info_frame,
            text=game["name"],
            font=("Helvetica", 12, "bold")
        )
        name_label.pack(anchor="w")
        
        # Temps de jeu
        playtime = game.get("playtime", 0)
        time_label = ctk.CTkLabel(
            info_frame,
            text=f"Temps de jeu: {format_playtime(playtime)}",
            font=("Helvetica", 10),
            text_color="gray"
        )
        time_label.pack(anchor="w")
        
        # Bouton de lancement
        launch_btn = ctk.CTkButton(
            game_frame,
            text="Lancer",
            command=lambda p=game["path"], idx=i: launch_game(p, idx),
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#2B2B2B",
            hover_color="#3B3B3B"
        )
        launch_btn.pack(side="left", padx=5)
        
        # Bouton de suppression
        delete_btn = ctk.CTkButton(
            game_frame,
            text="×",
            command=lambda idx=i: delete_game(idx),
            width=40,
            height=40,
            corner_radius=10,
            fg_color="#FF4444",
            hover_color="#FF6666"
        )
        delete_btn.pack(side="right", padx=5)

# Interface principale
root = ctk.CTk()
root.title("Game Launcher")
root.geometry("500x600")  # Augmenté la largeur pour accommoder le temps de jeu
root.configure(fg_color="#1A1A1A")

def on_closing():
    global should_monitor
    should_monitor = False
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Titre
title_label = ctk.CTkLabel(
    root,
    text="GAME LAUNCHER",
    font=("Helvetica", 24, "bold"),
    text_color="#FFFFFF"
)
title_label.pack(pady=20)

# Frame principal
frame = ctk.CTkFrame(root, fg_color="transparent")
frame.pack(fill="both", expand=True, padx=20, pady=10)

# Bouton d'ajout
add_btn = ctk.CTkButton(
    root,
    text="Ajouter un jeu",
    command=add_game,
    width=200,
    height=40,
    corner_radius=10,
    fg_color="#4CAF50",
    hover_color="#45a049"
)
add_btn.pack(pady=20)

# Charger les jeux
games = load_games()
refresh_buttons()

# Lancer l'application
root.mainloop()