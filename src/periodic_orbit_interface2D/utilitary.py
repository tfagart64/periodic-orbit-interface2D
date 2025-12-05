#%%Importations
import tkinter as tk
from tkinter import ttk
import numpy as np
import os
import pandas as pd

#%% General functions
def rgb_float_tuple_to_hex(rgb):
    r, g, b = rgb
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

def switch_axis(axis):
    if axis == 'x=0':
        new_axis = 'y=0'
    elif axis == 'y=0':
        new_axis = 'x=0'
    else:
        raise  ValueError(f"Invalid axis name: '{axis}'. Expected 'x=0' or 'y=0'.")
    
    return new_axis

def calculate_theta(x, y):
    """
    Calculates the standard trigonometric angle (0-360 degrees) for a point (x, y).
    The angle is measured counter-clockwise from the positive X-axis.
    """
    angle_rad = np.arctan2(y, x)
    angle_deg = np.degrees(angle_rad)
    return (angle_deg + 360) % 360 # Ensure angle is between 0 and 360

def calculate_delta(x, y, domain_location_id):
    """
    Calculates the angle delta relative to the bisector of the quadrant.
    The bisector is y=x for Q1, Q3 and y=-x for Q2, Q4.
    This angle is the deviation from the quadrant's main diagonal.
    """
    
    alpha_deg = (domain_location_id-1) * 90 + 45
    theta_deg = calculate_theta(x, y)
    delta_deg = alpha_deg - theta_deg

    return delta_deg

def ask_overwrite_action(setup_name):
    """
    Opens a personalized window with 3 options :
    Ouvre une fenêtre personnalisée avec 3 options :
    - Replace : replace file
    - Create new : create a new version with a numerical suffix
    - Cancel : cancel operation
    """
    dialog = tk.Toplevel()
    dialog.title("Existing file")
    dialog.geometry("350x150")
    dialog.grab_set()  # Bloque l'interaction avec la fenêtre principale

    ttk.Label(dialog, text=f" The setup '{setup_name}' already exists. What do you want to do ?").pack(pady=10)

    result = {"choice": None}

    def choose(option):
        result["choice"] = option
        dialog.destroy()

    ttk.Button(dialog, text="Replace", command=lambda: choose("replace")).pack(side=tk.LEFT, expand=True, padx=5, pady=20)
    ttk.Button(dialog, text="Create new", command=lambda: choose("new")).pack(side=tk.LEFT, expand=True, padx=5, pady=20)
    ttk.Button(dialog, text="Cancel", command=lambda: choose("cancel")).pack(side=tk.LEFT, expand=True, padx=5, pady=20)

    dialog.wait_window()
    return result["choice"]

def find_all_possible_setups(setup_folder):
    if not os.path.exists(setup_folder):
        return ["base"]

    csv_files = [f for f in os.listdir(setup_folder) if f.endswith(".csv")]
    csv_names = [os.path.splitext(os.path.basename(f))[0] for f in csv_files]
    if "base" in csv_names:
        csv_names.remove("base")
    
    # Always include "base" first
    return ["base"] + csv_names


def read_file_and_extract_dataframe(folder, filename, extension=".csv"):
    """
    Read a file contained in a folder and with a certain extension. Extract a dataframe from it.
    """
    file_path = os.path.join(folder, filename + extension)

    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return
    
    supported_extensions = {
        ".csv": pd.read_csv,
        # ".xlsx": pd.read_excel,
        # ".json": pd.read_json,
    }
    
    if extension in supported_extensions:
        df = supported_extensions[extension](file_path)
    else:
        raise ValueError(
            f"Unsupported file extension '{extension}'. "
            f"Supported extensions are: {list(supported_extensions.keys())}"
        )
    
    return df
