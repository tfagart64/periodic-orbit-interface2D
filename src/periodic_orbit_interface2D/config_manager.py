import os
import json
from platformdirs import user_config_dir
import tkinter as tk
from tkinter.filedialog import askdirectory

APP_NAME = "periodic-orbit-interface2D"

def get_config_path():
    config_dir = user_config_dir(APP_NAME)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(get_config_path(), "w") as f:
        json.dump(config, f, indent=4)

def get_setup_directory(mode):
    """
    mode: "straight" or "non_straight"
    """
    config = load_config()
    key = f"setup_directory_{mode}"

    # If the path already exists, return it
    if key in config and os.path.isdir(config[key]):
        return config[key]

    # Otherwise, ask the user
    root = tk.Tk()
    root.withdraw()
    path = askdirectory(title=f"Choose setup storage folder ({mode} mode)")
    root.destroy()

    if path:
        config[key] = path
        save_config(config)
        return path
    else:
        raise ValueError(f"No setup folder was selected for the mode {mode}.")

def change_setup_directory(mode):
    """
    Opens a dialog to let the user choose a new setup directory for the given mode.
    
    mode: "straight" or "non_straight"
    Returns the new directory path or None if cancelled.
    """

    config = load_config()
    key = f"setup_directory_{mode}"

    # Ask the user for a new folder
    root = tk.Tk()
    root.withdraw()
    new_path = askdirectory(title=f"Choose new setup storage folder ({mode} mode)")
    root.destroy()

    if new_path and os.path.isdir(new_path):
        config[key] = new_path
        save_config(config)
        return new_path

    return None

