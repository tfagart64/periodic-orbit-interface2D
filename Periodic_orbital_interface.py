#%%Importations
import tkinter as tk
from tkinter import ttk  # Using ttk for potentially more modern widgets
import numpy as np
import os
import pandas as pd

#%%Fonctions générales
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
    Ouvre une fenêtre personnalisée avec 3 options :
    - Replace : écraser le fichier
    - Create new : créer une nouvelle version avec suffixe numérique
    - Cancel : annuler l'opération
    """
    dialog = tk.Toplevel()
    dialog.title("Fichier existant")
    dialog.geometry("350x150")
    dialog.grab_set()  # Bloque l'interaction avec la fenêtre principale

    ttk.Label(dialog, text=f"Le setup '{setup_name}' existe déjà.\nQue voulez-vous faire ?").pack(pady=10)

    result = {"choice": None}

    def choose(option):
        result["choice"] = option
        dialog.destroy()

    ttk.Button(dialog, text="Replace", command=lambda: choose("replace")).pack(side=tk.LEFT, expand=True, padx=5, pady=20)
    ttk.Button(dialog, text="Create new", command=lambda: choose("new")).pack(side=tk.LEFT, expand=True, padx=5, pady=20)
    ttk.Button(dialog, text="Cancel", command=lambda: choose("cancel")).pack(side=tk.LEFT, expand=True, padx=5, pady=20)

    dialog.wait_window()
    return result["choice"]

#%%Class TKinter app
class Visualisation_app_straight:
  
    def __init__(self, root):
        self.root = root
        self.root.title("Interface for phase space observations")
        self.root.geometry("1700x1000")
        
        # Registry of frame → callback
        self.return_bindings = {}

        # Track current active binding
        self.active_callback = None

        # Global focus tracking
        self.root.bind_all("<FocusIn>", self._on_focus_in)
        self.root.bind_all("<FocusOut>", self._on_focus_out)
        
        # --- Main Layout Frames ---
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.left_frame, width=1000)

        self.middle_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.middle_frame, width=300)
        
        self.right_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.right_frame, width=400)

        # --- Canvas Frame (Left) ---
        self.canvas_frame = ttk.Frame(self.left_frame, relief=tk.SUNKEN, borderwidth=1)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize parameters
        self.base_system = "base_ABC_K1_K2"
        self.base_system = "base_DAMFC_K1_K2"
        self.base_system = "base_DAEFC_K1_K2"
        self.init_parameters()
        
        # Initial center coords
        self.center_coords = np.array([self.K2, self.K1])
        
        # Set canvas
        self.set_canvas() # This method is not changed, but called here
        
        # --- Toolbar Frame (Middle) ---
        self.toolbar_frame = ttk.LabelFrame(self.middle_frame, text="Tools", padding=10)
        self.toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.button_undo_focal_point = ttk.Button(self.toolbar_frame, text="Undo focal point", command=self.undo_focal_point)
        self.button_undo_focal_point.pack(fill=tk.X, pady=2)
        
        self.button_remove_initial_point = ttk.Button(self.toolbar_frame, text="Remove initial point", command=self.remove_initial_point)
        self.button_remove_initial_point.pack(fill=tk.X, pady=2)
        
        self.button_clear_canvas_points = ttk.Button(self.toolbar_frame, text="Clear points", command=self.clear_canvas_points)
        self.button_clear_canvas_points.pack(fill=tk.X, pady=2)
        
        self.button_save_setup = ttk.Button(self.toolbar_frame, text="Save setup", command=self.open_save_popup)
        self.button_save_setup.pack(fill=tk.X, pady=2)
        
        # Setup selection
        # Liste initiale au lancement
        self.setups = self.find_all_possible_setups()
        
        self.setup_strvar = tk.StringVar(value="base")
        ttk.Label(self.toolbar_frame, text="Setup selection :").pack(pady=5)
        self.select_setup_menu = ttk.OptionMenu(self.toolbar_frame, self.setup_strvar, self.setup_strvar.get(), *self.setups, command=self.apply_new_setup)
        self.select_setup_menu.pack(fill=tk.X, pady=2)
        
        # Quand on clique → mettre à jour la liste
        self.select_setup_menu.bind("<Button-1>", self.update_setup_menu)
        
        # Movement mode selection
        self.dragging_mode = tk.StringVar(value="Free")
        self.dragging_modes = ["Free", "Horizontal", "Vertical", "Linear", "Circular"]
        ttk.Label(self.toolbar_frame, text="Movement Mode :").pack(pady=5)
        self.dragging_mode_menu = ttk.OptionMenu(self.toolbar_frame, self.dragging_mode, self.dragging_mode.get(), *self.dragging_modes)
        self.dragging_mode_menu.pack(fill=tk.X, pady=2)
        
        
        
        # --- Center Coordinates Input (Middle) ---
        self.create_center_input_frame()
        
        # --- Canvas Limits Input (Middle) ---
        self.create_dimensions_input_frame()
        
        # --- Point Input Frame (Middle) ---
        self.create_point_input_frame()
        
        
        
        # --- Results Frame (Right) ---
        self.results_frame = ttk.LabelFrame(self.right_frame, text="Results", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.results_label = ttk.Label(self.results_frame, text="No results yet.")
        self.results_label.pack(fill=tk.Y, expand=False)
        
        # Initializations
        self.space_grid_step = 1.0
        self.major_tick_step = 1.0
        
        self.point_size = 10
        self.focal_points_colors_RGB = ((0.8,0.7,0.9), (0.9,0.8,0.6), (0.7,0.9,0.9), (0.95,0.75,0.75))
        self.canvas_point_ids = []
        self.focal_points = {}
        
        self.canvas_initial_point_id = None
        self.initial_point = {}
        
        self.canvas_lim_line_ids = []
        self.canvas_norm_line_ids = []
        self.color_lim_lines = "red"
        self.color_norm_lines = "black"
        self.line_width_lim = 8
        self.line_width_norm = 2

        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragged_item_id = None
        self.original_space_coords = None
        self.dragged_point_type = None
        self.dragging_focal_point_id = None
        
        self.setup_name = self.base_system
        
        # New variables for point input functionality
        self.selected_point_id = None  # Stores the canvas ID of the currently selected point
        self.selected_point_type = None # 'focal' or 'initial'
        self.selected_focal_glass_id = None # Stores the glass_point_id if a focal point is selected
        
        self.initialize_focal_points()
        
        self.save_setup(self.setup_name, is_base_save=True)
        
    def init_parameters(self):
        if self.base_system == "base_ABC_K1_K2":
            self.gamma = 0.177616984486787
            self.K1 = 1.15922127869615
            self.K2 = 1.88631980371717
            
            self.A = 1.1855
            self.B = 4.5515
            self.C = 1.4193
            
            # Define initial numerical limits BEFORE creating StringVars for them
            self.min_space_x = 0.
            self.max_space_x = 7.
            self.min_space_y = 0.
            self.max_space_y = 3.
        
                
        if self.base_system == "base_DAEFC_K1_K2":
            self.gamma = 0.177616984486787
            self.K1 = 5.
            self.K2 = 3.5
            
            self.D = 4.
            self.A = 2.
            self.E = 3.
            
            self.F = 4.
            self.C = 2.
            
            # Define initial numerical limits BEFORE creating StringVars for them
            self.min_space_x = 0.
            self.max_space_x = 7.
            self.min_space_y = 3.
            self.max_space_y = 7.
        
        if self.base_system == "base_DAMFC_K1_K2":
            self.gamma = 0.177616984486787
            self.K1 = 2.5
            self.K2 = 3.5
            
            self.D = 4.
            self.A = 2.
            self.M = 0.25
            
            self.F = 2.
            self.C = 1.
            
            # Define initial numerical limits BEFORE creating StringVars for them
            self.min_space_x = 0.
            self.max_space_x = 8.
            self.min_space_y = 0.
            self.max_space_y = 5.
            
            
            # Tests
            K1, K2, D, A, M, F, C = self.K1, self.K2, self.D, self.A, self.M, self.F, self.C
            h1_test = - (K2*A*(F-K1)) / (D*C)
            print(h1_test, h1_test + K2)
            
            h2_test = (F-K1) / (1 + (C*(D+A)*(D*M-K2)) / (K2*A*(F+C-K1)))
            print(h2_test, h2_test+ K1)
            
            h3_test = - (K2*A*(F+C-K1)) / ((D+A)*C)
            print(h3_test, h3_test + K2)
            
            h4_test = (F+C-K1) / (1 + (D*C*(D+A-K2)) / (K2*A*(F-K1)))
            print(h4_test, h4_test+ K1)
            
            amp_Xps_test = (K2*A) / (D+A) * (1 - (A*(F-K1)) / (D*C))
            print('amp_Xps_test', amp_Xps_test)
            
            amp_Xpu_test = (K2*A*(F-K1)*(F+C-K1)*C*D*(D+A)*(1-M)) / ((K2*A*(F+C-K1)+C*(D+A)*(M*D-K2)) * (K2*A*(F+C-K1)+C*(D+A)*(D-K2)))
            print('amp_Xps_test', amp_Xpu_test)
        
    def _draw_grid_and_axes(self, event=None):
        """
        Dessine la grille, les axes, les graduations et les étiquettes sur le canevas.
        Cette fonction est appelée chaque fois que le canevas est redimensionné.
        MODIFIED: Le dessin est maintenant relatif au self.center_coords.
        """
        # Supprime tous les éléments précédents de la grille, des axes et des étiquettes
        self.canvas.delete("grid_line")
        self.canvas.delete("axis")
        self.canvas.delete("tick_label")
        self.canvas.delete("quadrant_bg") # Supprime les fonds de quadrant

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 0 or canvas_height <= 0:
            return

        self.pixels_per_unit_x = canvas_width / (self.max_space_x - self.min_space_x)
        self.pixels_per_unit_y = canvas_height / (self.max_space_y - self.min_space_y)
        
        # Calcule les coordonnées pixel sur le canevas du centre d'oscillation
        center_x_on_canvas, center_y_on_canvas = self.get_canvas_coords_from_absolute_space_coords(self.center_coords[0], self.center_coords[1])

        # --- Dessin des fonds de quadrants ---
        # Les quadrants sont définis par rapport au centre d'oscillation
        # Quadrant 1 (x > center_x, y > center_y) - Domaine 1
        self.canvas.create_rectangle(
            center_x_on_canvas, 0, canvas_width, center_y_on_canvas,
            fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[0]),
            outline="", tags="quadrant_bg"
        )
        # Quadrant 2 (x < center_x, y > center_y) - Domaine 2
        self.canvas.create_rectangle(
            0, 0, center_x_on_canvas, center_y_on_canvas,
            fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[1]),
            outline="", tags="quadrant_bg"
        )
        # Quadrant 3 (x < center_x, y < center_y) - Domaine 3
        self.canvas.create_rectangle(
            0, center_y_on_canvas, center_x_on_canvas, canvas_height,
            fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[2]),
            outline="", tags="quadrant_bg"
        )
        # Quadrant 4 (x > center_x, y < center_y) - Domaine 4
        self.canvas.create_rectangle(
            center_x_on_canvas, center_y_on_canvas, canvas_width, canvas_height,
            fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[3]),
            outline="", tags="quadrant_bg"
        )

        # --- Dessin de la Grille ---
        # Les lignes de grille sont dessinées pour l'espace absolu
        for x_absolute_space in np.arange(self.min_space_x, self.max_space_x + self.space_grid_step, self.space_grid_step):
            x_px = (x_absolute_space - self.min_space_x) * self.pixels_per_unit_x
            self.canvas.create_line(x_px, 0, x_px, canvas_height, fill="black", tags="grid_line")
    
        for y_absolute_space in np.arange(self.min_space_y, self.max_space_y + self.space_grid_step, self.space_grid_step):
            y_px = (self.max_space_y - y_absolute_space) * self.pixels_per_unit_y
            self.canvas.create_line(0, y_px, canvas_width, y_px, fill="black", tags="grid_line")

        # --- Dessin des Axes ---
        # Les axes sont dessinés à la position du centre d'oscillation sur le canevas
        self.canvas.create_line(0, center_y_on_canvas, canvas_width, center_y_on_canvas, fill="black", width=2, tags="axis") # Axe X
        self.canvas.create_line(center_x_on_canvas, 0, center_x_on_canvas, canvas_height, fill="black", width=2, tags="axis") # Axe Y

        # Dessin du point central (anciennement l'origine)
        self.canvas.create_oval(center_x_on_canvas - 3, center_y_on_canvas - 3, center_x_on_canvas + 3, center_y_on_canvas + 3, fill="black", tags="axis")

        # --- Dessin des Graduations et des Étiquettes ---
        tick_length = 5

        # Graduations et étiquettes de l'axe X
        for x_absolute_space in np.arange(self.min_space_x, self.max_space_x + self.major_tick_step, self.major_tick_step):
            x_px = (x_absolute_space - self.min_space_x) * self.pixels_per_unit_x
            self.canvas.create_line(x_px, center_y_on_canvas - tick_length, x_px, center_y_on_canvas + tick_length, fill="black", tags="axis")
            # Étiquette les graduations, mais pas la coordonnée X du centre si elle est déjà étiquetée par le point central
            if abs(x_absolute_space - self.center_coords[0]) > 1e-6: # Vérifie si ce n'est pas le centre
                self.canvas.create_text(x_px, center_y_on_canvas + tick_length + 8, text=f"{x_absolute_space:.2f}", fill="black", tags="tick_label")

        # Graduations et étiquettes de l'axe Y
        for y_absolute_space in np.arange(self.min_space_y, self.max_space_y + self.major_tick_step, self.major_tick_step):
            y_px = (self.max_space_y - y_absolute_space) * self.pixels_per_unit_y
            self.canvas.create_line(center_x_on_canvas - tick_length, y_px, center_x_on_canvas + tick_length, y_px, fill="black", tags="axis")
            # Étiquette les graduations, mais pas la coordonnée Y du centre
            if abs(y_absolute_space - self.center_coords[1]) > 1e-6: # Vérifie si ce n'est pas le centre
                self.canvas.create_text(center_x_on_canvas - tick_length - 8, y_px, text=f"{y_absolute_space:.2f}", fill="black", anchor="e", tags="tick_label")

        # Étiquette pour le centre de l'oscillation
        self.canvas.create_text(center_x_on_canvas + 8, center_y_on_canvas + 8, text=f"({self.center_coords[0]:.2f},{self.center_coords[1]:.2f})", fill="black", tags="tick_label")

        # Étiquettes des axes (X et Y)
        self.canvas.create_text(canvas_width - 15, center_y_on_canvas + 15, text="X", fill="black", font=("Arial", 10, "bold"), tags="axis")
        self.canvas.create_text(center_x_on_canvas + 15, 15, text="Y", fill="black", font=("Arial", 10, "bold"), tags="axis")
    
    def set_canvas(self):
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.reload_canvas)
        self.canvas.bind("<Button-1>", self.on_left_click) # Modified to handle dragging initiation
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag) # New binding for dragging
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release) # New binding for releasing
        self.canvas.bind("<Button-3>", self.add_initial_point)
        
    
    def initialize_focal_points(self):
        """
        Initializes four focal points with predefined absolute coordinates.
        This function clears any existing focal points and then creates new ones.
        """
        self.canvas_point_ids = []
        self.focal_points = {} # Clear the dictionary of focal points

        if self.base_system == 'base_ABC_K1_K2':
            initial_abs_coords = {
            1: np.array([self.A, self.C]), # glass_point_id 1 (attached to TR, located in TL)
            2: np.array([0., 0.]), # glass_point_id 2 (attached to TL, located in BL)
            3: np.array([self.B, 0.]),  # glass_point_id 3 (attached to BL, located in BR)
            4: np.array([self.A + self.B, self.C])}    # glass_point_id 4 (attached to BR, located in TR)
         
        elif self.base_system == 'base_DAEFC_K1_K2':
            initial_abs_coords = {
            1: np.array([self.D + self.A - self.E, self.F + self.C]), # glass_point_id 1 (attached to TR, located in TL)
            2: np.array([self.D - self.E, self.F]), # glass_point_id 2 (attached to TL, located in BL)
            3: np.array([self.D, self.F]),  # glass_point_id 3 (attached to BL, located in BR)
            4: np.array([self.D + self.A, self.F + self.C])}    # glass_point_id 4 (attached to BR, located in TR)
         
        elif self.base_system == 'base_DAMFC_K1_K2':
            initial_abs_coords = {
            1: np.array([self.M * (self.D + self.A), self.F + self.C]), # glass_point_id 1 (attached to TR, located in TL)
            2: np.array([self.M * self.D, self.F]), # glass_point_id 2 (attached to TL, located in BL)
            3: np.array([self.D, self.F]),  # glass_point_id 3 (attached to BL, located in BR)
            4: np.array([self.D + self.A, self.F + self.C])}    # glass_point_id 4 (attached to BR, located in TR)
        
        else:
            print('No setup associated with this base system name')

        for glass_point_id in sorted(initial_abs_coords.keys()):
            abs_space_coords = initial_abs_coords[glass_point_id]
            
            # Calculate relative coordinates based on the current center
            rel_space_coords = abs_space_coords - self.center_coords
        
            # Determine the domain location ID for angle calculations
            domain_location_id = self.classify_point_per_domain_location(abs_space_coords[0], abs_space_coords[1])
            if domain_location_id is None:
                # This should ideally not happen with carefully chosen initial coordinates
                self.show_notification(f"Error: Initial focal point {glass_point_id} is on an axis.", bg_color='red')
                continue # Skip this point if it's problematic
        
            # Calculate angles
            angle_theta = calculate_theta(rel_space_coords[0], rel_space_coords[1])
            angle_delta = calculate_delta(rel_space_coords[0], rel_space_coords[1], domain_location_id)
        
            # Convert space coordinates to canvas coordinates
            x_canvas, y_canvas = self.get_canvas_coords_from_absolute_space_coords(abs_space_coords[0], abs_space_coords[1])
        
            # Create the oval on the canvas
            canva_point_id = self.canvas.create_oval(
                x_canvas - self.point_size, y_canvas - self.point_size,
                x_canvas + self.point_size, y_canvas + self.point_size,
                fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[glass_point_id - 1]),
                outline="", width=1 # No outline initially, handled by update_point_input_fields
            )
            self.canvas_point_ids.append(canva_point_id)
        
            # Store point data
            self.focal_points[glass_point_id] = {
                'canva_point_id': canva_point_id,
                'canvas_coords': np.array([x_canvas, y_canvas]),
                'abs_space_coords': abs_space_coords,
                'rel_space_coords': rel_space_coords,
                'angle_theta': angle_theta,
                'angle_delta': angle_delta
            }
        
        # After all points are created, update the UI
        self.compute_all_self_attributes()
        self.update_canvas_limit_traj()
        self.update_results_frame()
        self.update_point_input_fields() # To ensure the input fields are populated and outline is correct
      
        
    #%%Utilitary functions
    def get_absolute_space_coords_from_canvas_coords(self, canvas_x, canvas_y):
        """
        Convertit les coordonnées en pixels du canevas en coordonnées absolues de notre système "espace".
        """
        width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
    
        pixels_per_unit_x = width / (self.max_space_x - self.min_space_x)
        pixels_per_unit_y = canvas_height / (self.max_space_y - self.min_space_y)
    
        x_absolute_space = self.min_space_x + (canvas_x / pixels_per_unit_x)
        y_absolute_space = self.max_space_y - (canvas_y / pixels_per_unit_y)
    
        return x_absolute_space, y_absolute_space

    def get_canvas_coords_from_absolute_space_coords(self, x_absolute_space, y_absolute_space):
        """
        Convertit les coordonnées absolues du système "espace" en coordonnées en pixels sur le canevas.
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if not hasattr(self, 'pixels_per_unit_x') or canvas_width == 0 or canvas_height == 0:
            self.pixels_per_unit_x = canvas_width / (self.max_space_x - self.min_space_x) if (self.max_space_x - self.min_space_x) != 0 else 1
            self.pixels_per_unit_y = canvas_height / (self.max_space_y - self.min_space_y) if (self.max_space_y - self.min_space_y) != 0 else 1

        canvas_x = (x_absolute_space - self.min_space_x) * self.pixels_per_unit_x
        canvas_y = (self.max_space_y - y_absolute_space) * self.pixels_per_unit_y
    
        return canvas_x, canvas_y
    
    
    def classify_point_per_domain_location(self, x_absolute_space, y_absolute_space, is_focal_point=True):
        """
        Classifies a point into its real-world geometric domain (quadrant) relative to self.center_coords.
        Takes ABSOLUTE space coordinates as input.
        Domain 1: x > center_x, y > center_y (Top-Right)
        Domain 2: x < center_x, y > center_y (Top-Left)
        Domain 3: x < center_x, y < center_y (Bottom-Left)
        Domain 4: x > center_x, y < center_y (Bottom-Right)

        Returns None if the point is on an axis relative to the center.
        """
        if not is_focal_point and abs(x_absolute_space - self.center_coords[0]) < 1e-9 and abs(y_absolute_space - self.center_coords[1]) < 1e-9:
            self.show_notification("Initial point is at the crossing of both delimitations", bg_color='red')
            return None
        elif is_focal_point and (abs(x_absolute_space - self.center_coords[0]) < 1e-9 or abs(y_absolute_space - self.center_coords[1]) < 1e-9):
            self.show_notification("Point is on the frontier of two domains", bg_color='red')
            return None
        elif x_absolute_space > self.center_coords[0] and y_absolute_space >= self.center_coords[1]:
            domain_id = 1
        elif x_absolute_space <= self.center_coords[0] and y_absolute_space > self.center_coords[1]:
            domain_id = 2
        elif x_absolute_space < self.center_coords[0] and y_absolute_space <= self.center_coords[1]:
            domain_id = 3
        else: # x_absolute_space > self.center_coords[0] and y_absolute_space < self.center_coords[1]
            domain_id = 4
        return domain_id
    
    def classify_point_per_domain_attached(self, x_absolute_space, y_absolute_space):
        """
        Classifies a focal point to its 'attached' domain (glass_point_id) relative to self.center_coords.
        Takes ABSOLUTE space coordinates as input.
        This follows the rule:
        - A point in Domain 1 (TR) is 'attached' to Domain 4 (BR)
        - A point in Domain 2 (TL) is 'attached' to Domain 1 (TR)
        - A point in Domain 3 (BL) is 'attached' to Domain 2 (TL)
        - A point in Domain 4 (BR) is 'attached' to Domain 3 (BL)

        Returns None if the point is on an axis relative to the center.
        """
        domain_location = self.classify_point_per_domain_location(x_absolute_space, y_absolute_space)
        if domain_location is None:
            return None
        
        # Determine the attached glass_point_id based on the location
        if domain_location == 1: # Located in TR, attached to BR
            glass_point_id = 4
        elif domain_location == 2: # Located in TL, attached to TR
            glass_point_id = 1
        elif domain_location == 3: # Located in BL, attached to TL
            glass_point_id = 2
        elif domain_location == 4: # Located in BR, attached to BL
            glass_point_id = 3
        
        return glass_point_id
    
    def find_glass_point_id_from_canvas_id(self, canva_point_id):
        """
        Recherche et retourne le glass_point_id associé à un canva_point_id donné.
        Retourne None si aucun point ne correspond.
        """
        for glass_point_id, data in self.focal_points.items():
            if data['canva_point_id'] == canva_point_id:
                return glass_point_id
        return None
    #%% Focus handling
    def register_return_binding(self, frame, callback):
        """Register a frame so Return runs its callback when focused."""
        self.return_bindings[frame] = callback
        
    def _on_focus_in(self, event):
        """When something gets focus, decide if Return should be bound."""
        widget = event.widget
    
        # Sécurisation : ignorer si widget est None ou une string (ex: '__tk__messagebox')
        if widget is None or isinstance(widget, str):
            self._unbind_return()
            return
    
        for frame, callback in self.return_bindings.items():
            if self._is_inside_widget(widget, frame):
                # Bind Return to the frame’s callback
                if self.active_callback != callback:
                    self.root.bind("<Return>", lambda e: callback())
                    self.active_callback = callback
                return
    
        # If no match, ensure Return is unbound
        self._unbind_return()
    
    def _unbind_return(self):
        if self.active_callback:
            self.root.unbind("<Return>")
            self.active_callback = None
    
    def _on_focus_out(self, event):
        """Check if focus left a registered frame; if so, unbind Return."""
        try:
            new_focus = self.root.focus_get()
        except Exception:
            new_focus = None
    
        # Cas où focus est un identifiant de widget (str) → ignorer
        if isinstance(new_focus, str):
            self._unbind_return()
            return
    
        for frame in self.return_bindings:
            if self._is_inside_widget(new_focus, frame):
                return  # Still inside a registered frame → keep binding
        self._unbind_return()
    
    
    @staticmethod
    def _is_inside_widget(widget, container):
        """Check if widget is inside container (or is the container)."""
        # Protection si widget est None ou une string
        if widget is None or isinstance(widget, str):
            return False
    
        while widget is not None:
            if widget == container:
                return True
            widget = widget.master
        return False

    #%%Button linked functions
    def on_left_click(self, event):
        """
        Handles left-click events on the canvas.
        Differentiates between starting a drag and selecting a point for input.
        """
        item = self.canvas.find_closest(event.x, event.y)
        
        # Check if the clicked item is a point (focal or initial)
        # item[0] is the canvas ID of the closest item
        if item and (item[0] in self.canvas_point_ids or item[0] == self.canvas_initial_point_id):
            bbox = self.canvas.bbox(item[0])
            if bbox: # Ensure item exists and has a bounding box
                # Check if click is within point's bounds (approximate)
                if bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
                    # This is a click on an existing point
                    self.start_drag(event, item[0]) # Start dragging
                    
                    # Also select the point for input fields
                    self.selected_point_id = item[0]
                    if item[0] == self.canvas_initial_point_id:
                        self.selected_point_type = 'initial'
                        self.selected_focal_glass_id = None
                    else:
                        self.selected_point_type = 'focal'
                        self.selected_focal_glass_id = self.find_glass_point_id_from_canvas_id(item[0])
                    self.update_point_input_fields() # This will update outline without redrawing all points
                    return # Point was clicked, don't add new focal point
        
        # If no point was clicked for dragging or selection, add a new focal point
        self.add_focal_point(event)
    
    def start_drag(self, event, item_id):
        self.is_dragging = True
        self.dragged_item_id = item_id
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # Determine if it's a focal point or initial point
        if item_id == self.canvas_initial_point_id:
            self.dragged_point_type = 'initial'
            # original_space_coords are already relative to center
            self.original_space_coords = self.initial_point['rel_space_coords'].copy() 
        else:
            # Find the glass_point_id for the focal point
            for gp_id, data in self.focal_points.items():
                if data['canva_point_id'] == item_id:
                    self.dragged_point_type = 'focal'
                    # original_space_coords are already relative to center
                    self.original_space_coords = data['rel_space_coords'].copy() 
                    self.dragging_focal_point_id = gp_id # Store the specific focal point ID
                    break
        self.canvas.bind("<Motion>", self.on_mouse_drag)

    # MODIFIED EXISTING FUNCTION
    def on_mouse_drag(self, event):
        """
        Handles mouse drag events for moving points.
        Updates point coordinates directly on the canvas and refreshes UI.
        Does NOT recreate points during drag.
        """
        if not self.is_dragging or self.dragged_item_id is None:
            return

        current_x_canvas, current_y_canvas = event.x, event.y
        # Get raw new absolute space coordinates from canvas
        x_absolute_new_raw, y_absolute_new_raw = self.get_absolute_space_coords_from_canvas_coords(current_x_canvas, current_y_canvas)

        # Get original space coordinates (relative to center) of the dragged point
        # self.original_space_coords holds the relative coordinates when drag started
        x_orig_relative, y_orig_relative = self.original_space_coords
        # Convert original relative to absolute for quadrant constraint check
        x_orig_absolute = x_orig_relative + self.center_coords[0]
        y_orig_absolute = y_orig_relative + self.center_coords[1]

        # Determine if we need to apply a quadrant constraint
        apply_quadrant_constraint = False
        constraining_domain_id = None # This will be the location domain for focal points

        if self.dragged_point_type == 'focal':
            apply_quadrant_constraint = True
            # Use the original point's *absolute* location domain for constraint
            constraining_domain_id = self.classify_point_per_domain_location(x_orig_absolute, y_orig_absolute)
            if constraining_domain_id is None:
                # This should ideally not happen if a focal point was properly placed
                self.show_notification("Focal point cannot be dragged from an axis.", bg_color='red')
                # Reset dragging state to prevent further issues
                self.on_mouse_release(event)
                return

        # Step 1: Clamp the raw new absolute coordinates based on quadrant constraint (only for focal points)
        x_absolute_clamped = x_absolute_new_raw
        y_absolute_clamped = y_absolute_new_raw

        # Strict quadrant clamping for focal points: avoid axes
        if apply_quadrant_constraint and constraining_domain_id is not None:
            epsilon = 1e-6 

            # Clamping relative to self.center_coords
            if constraining_domain_id == 1: # Q1: x > center_x, y > center_y
                x_absolute_clamped = max(self.center_coords[0] + epsilon, x_absolute_clamped)
                y_absolute_clamped = max(self.center_coords[1] + epsilon, y_absolute_clamped)
            elif constraining_domain_id == 2: # Q2: x < center_x, y > center_y
                x_absolute_clamped = min(self.center_coords[0] - epsilon, x_absolute_clamped)
                y_absolute_clamped = max(self.center_coords[1] + epsilon, y_absolute_clamped)
            elif constraining_domain_id == 3: # Q3: x < center_x, y < center_y
                x_absolute_clamped = min(self.center_coords[0] - epsilon, x_absolute_clamped)
                y_absolute_clamped = min(self.center_coords[1] - epsilon, y_absolute_clamped)
            elif constraining_domain_id == 4: # Q4: x > center_x, y < center_y
                x_absolute_clamped = max(self.center_coords[0] + epsilon, x_absolute_clamped)
                y_absolute_clamped = min(self.center_coords[1] - epsilon, y_absolute_clamped)

        # Step 2: Apply dragging mode constraints to the clamped absolute coordinates
        mode = self.dragging_mode.get()
        x_absolute_mode_adjusted, y_absolute_mode_adjusted = x_absolute_clamped, y_absolute_clamped

        if mode == "Horizontal":
            y_absolute_mode_adjusted = y_orig_absolute # Keep original absolute Y
        elif mode == "Vertical":
            x_absolute_mode_adjusted = x_orig_absolute # Keep original absolute X
        elif mode == "Linear":
            # Vector from center to original point (relative)
            V_orig_relative_to_center = self.original_space_coords
            
            if np.linalg.norm(V_orig_relative_to_center) < 1e-6: # Original point is at or very near the center
                x_absolute_mode_adjusted, y_absolute_mode_adjusted = x_orig_absolute, y_orig_absolute # Keep it fixed
            else:
                # Vector from center to current clamped point (relative)
                P_clamped_relative_to_center = np.array([x_absolute_clamped, y_absolute_clamped]) - self.center_coords
                
                dot_product = np.dot(P_clamped_relative_to_center, V_orig_relative_to_center)
                norm_squared_V = np.dot(V_orig_relative_to_center, V_orig_relative_to_center) 
                
                if norm_squared_V > 1e-10: 
                    t = dot_product / norm_squared_V
                    # Calculate new point relative to center, then add center back to get absolute
                    x_absolute_mode_adjusted = self.center_coords[0] + t * V_orig_relative_to_center[0]
                    y_absolute_mode_adjusted = self.center_coords[1] + t * V_orig_relative_to_center[1]
                else: 
                    x_absolute_mode_adjusted, y_absolute_mode_adjusted = x_orig_absolute, y_orig_absolute 
        elif mode == "Circular":
            # Distance from center to original point (relative)
            dist_orig = np.linalg.norm(self.original_space_coords)
            if dist_orig < 1e-6: # Original point is at or near center, circular dragging is ill-defined
                x_absolute_mode_adjusted, y_absolute_mode_adjusted = x_orig_absolute, y_orig_absolute # Keep it fixed
            else:
                # Current point relative to center
                current_point_relative_to_center = np.array([x_absolute_clamped, y_absolute_clamped]) - self.center_coords
                current_dist = np.linalg.norm(current_point_relative_to_center)
                if current_dist < 1e-6: # If current point is at or near origin, snap to original
                    x_absolute_mode_adjusted, y_absolute_mode_adjusted = x_orig_absolute, y_orig_absolute
                else:
                    scale_factor = dist_orig / current_dist
                    # Calculate new point relative to center, then add center back to get absolute
                    x_absolute_mode_adjusted = self.center_coords[0] + current_point_relative_to_center[0] * scale_factor
                    y_absolute_mode_adjusted = self.center_coords[1] + current_point_relative_to_center[1] * scale_factor

        # Step 3: Re-apply strict quadrant clamp if applicable (for focal points)
        x_absolute_final, y_absolute_final = x_absolute_mode_adjusted, y_absolute_mode_adjusted

        if apply_quadrant_constraint and constraining_domain_id is not None:
            epsilon = 1e-6 

            # Re-clamping relative to self.center_coords
            if constraining_domain_id == 1: # Q1: x > center_x, y > center_y
                x_absolute_final = max(self.center_coords[0] + epsilon, x_absolute_final)
                y_absolute_final = max(self.center_coords[1] + epsilon, y_absolute_final)
            elif constraining_domain_id == 2: # Q2: x < center_x, y > center_y
                x_absolute_final = min(self.center_coords[0] - epsilon, x_absolute_final)
                y_absolute_final = max(self.center_coords[1] + epsilon, y_absolute_final)
            elif constraining_domain_id == 3: # Q3: x < center_x, y < center_y
                x_absolute_final = min(self.center_coords[0] - epsilon, x_absolute_final)
                y_absolute_final = min(self.center_coords[1] - epsilon, y_absolute_final)
            elif constraining_domain_id == 4: # Q4: x > center_x, y < center_y
                x_absolute_final = max(self.center_coords[0] + epsilon, x_absolute_final)
                y_absolute_final = min(self.center_coords[1] - epsilon, y_absolute_final)

        # Convert final absolute space coords back to canvas coordinates for drawing
        new_x_canvas, new_y_canvas = self.get_canvas_coords_from_absolute_space_coords(x_absolute_final, y_absolute_final)

        # Update the point's position on the canvas using canvas.coords()
        self.canvas.coords(self.dragged_item_id, 
                           new_x_canvas - self.point_size, new_y_canvas - self.point_size,
                           new_x_canvas + self.point_size, new_y_canvas + self.point_size)

        # Update the stored coordinates of the point (now stored relative to center)
        if self.dragged_point_type == 'initial':
            new_domain_id = self.classify_point_per_domain_location(x_absolute_final, y_absolute_final, is_focal_point=False)
            if new_domain_id is None: # If point moved to center/axis, disallow for initial point.
                 # Revert to original coordinates for the initial point for the current drag.
                self.initial_point['rel_space_coords'] = self.original_space_coords
                self.initial_point['abs_space_coords'] = self.original_space_coords + self.center_coords
                orig_canvas_x, orig_canvas_y = self.get_canvas_coords_from_absolute_space_coords(self.initial_point['abs_space_coords'][0], self.initial_point['abs_space_coords'][1])
                self.canvas.coords(self.dragged_item_id, 
                                   orig_canvas_x - self.point_size, orig_canvas_y - self.point_size,
                                   orig_canvas_x + self.point_size, orig_canvas_y + self.point_size)
                self.show_notification("Initial point cannot be dragged to the center.", bg_color='red')
                self.update_canvas_normal_traj()
                self.on_mouse_release(event) # End drag
                return

            self.initial_point['canvas_coords'] = np.array([new_x_canvas, new_y_canvas])
            self.initial_point['rel_space_coords'] = np.array([x_absolute_final - self.center_coords[0], y_absolute_final - self.center_coords[1]])
            self.initial_point['abs_space_coords'] = np.array([x_absolute_final, y_absolute_final]) # Update absolute
            self.initial_point['domain_id'] = new_domain_id


        else: # dragged_point_type == 'focal'
            point_data = self.focal_points[self.dragging_focal_point_id]
            
            current_focal_location_id = self.classify_point_per_domain_location(x_absolute_final, y_absolute_final)
            # Revert if focal point tries to leave its glass_point_id quadrant
            if current_focal_location_id is None or self.classify_point_per_domain_attached(x_absolute_final, y_absolute_final) != self.dragging_focal_point_id:
                # Revert to original coordinates for the focal point for the current drag.
                point_data['rel_space_coords'] = self.original_space_coords
                point_data['abs_space_coords'] = self.original_space_coords + self.center_coords
                orig_canvas_x, orig_canvas_y = self.get_canvas_coords_from_absolute_space_coords(point_data['abs_space_coords'][0], point_data['abs_space_coords'][1])
                self.canvas.coords(self.dragged_item_id, 
                                   orig_canvas_x - self.point_size, orig_canvas_y - self.point_size,
                                   orig_canvas_x + self.point_size, orig_canvas_y + self.point_size)
                self.show_notification(f"Focal point {self.dragging_focal_point_id} cannot be dragged outside its quadrant or onto an axis.", bg_color='red')
                self.update_canvas_limit_traj()
                self.update_canvas_normal_traj()
                self.on_mouse_release(event) # End drag
                return
            
            point_data['canvas_coords'] = np.array([new_x_canvas, new_y_canvas])
            point_data['rel_space_coords'] = np.array([x_absolute_final - self.center_coords[0], y_absolute_final - self.center_coords[1]])
            point_data['abs_space_coords'] = np.array([x_absolute_final, y_absolute_final]) # Update absolute
            
            x_relative_final = x_absolute_final - self.center_coords[0]
            y_relative_final = y_absolute_final - self.center_coords[1]
            
            point_data['angle_theta'] = calculate_theta(x_relative_final, y_relative_final)
            point_data['angle_delta'] = calculate_delta(x_relative_final, y_relative_final, current_focal_location_id)


        # Recalculate and redraw trajectories
        self.setup_strvar.set("")
        self.compute_all_self_attributes()
        self.update_canvas_limit_traj()
        self.update_canvas_normal_traj()
        self.update_results_frame()
        self.update_point_input_fields() # Update fields during drag (now safe from full redraw)

    # MODIFIED EXISTING FUNCTION
    def on_mouse_release(self, event):
        """
        Handles mouse release events after dragging.
        Resets dragging flags and ensures input fields are updated.
        """
        self.is_dragging = False
        self.dragged_item_id = None
        self.original_space_coords = None
        self.dragged_point_type = None
        self.dragging_focal_point_id = None
        self.canvas.unbind("<Motion>") # Unbind motion event after release
        self.update_point_input_fields() # Ensure fields are updated after release (and outline is correct)

    def add_focal_point(self, event):
        """
        Adds a new focal point to the canvas based on a click event.
        Handles quadrant classification and updates UI.
        """
        # Only add a new focal point if not dragging an existing one
        if self.is_dragging:
            return

        x_canvas, y_canvas = event.x, event.y
        # Get absolute space coordinates from canvas click
        x_absolute_space, y_absolute_space = self.get_absolute_space_coords_from_canvas_coords(x_canvas, y_canvas)
        
        # Determine the actual location domain for angle calculations and strict quadrant check
        domain_location_id = self.classify_point_per_domain_location(x_absolute_space, y_absolute_space)
        if domain_location_id is None:
            self.show_notification("Focal point cannot be placed on an axis.", bg_color='red')
            return

        # Use the 'attached' classification for focal points (glass_point_id)
        glass_point_id = self.classify_point_per_domain_attached(x_absolute_space, y_absolute_space)
        
        # Ensure strict placement off axes for focal points
        epsilon = 1e-6
        # Clamping absolute coordinates relative to self.center_coords
        if domain_location_id == 1: # Q1: x > center_x, y > center_y
            x_absolute_space = max(self.center_coords[0] + epsilon, x_absolute_space)
            y_absolute_space = max(self.center_coords[1] + epsilon, y_absolute_space)
        elif domain_location_id == 2: # Q2: x < center_x, y > center_y
            x_absolute_space = min(self.center_coords[0] - epsilon, x_absolute_space)
            y_absolute_space = max(self.center_coords[1] + epsilon, y_absolute_space)
        elif domain_location_id == 3: # Q3: x < center_x, y < center_y
            x_absolute_space = min(self.center_coords[0] - epsilon, x_absolute_space)
            y_absolute_space = min(self.center_coords[1] - epsilon, y_absolute_space)
        elif domain_location_id == 4: # Q4: x > center_x, y < center_y
            x_absolute_space = max(self.center_coords[0] + epsilon, x_absolute_space)
            y_absolute_space = min(self.center_coords[1] - epsilon, y_absolute_space)

        # Recalculate canvas coordinates based on potentially clamped absolute space coordinates
        x_canvas, y_canvas = self.get_canvas_coords_from_absolute_space_coords(x_absolute_space, y_absolute_space)

        if glass_point_id is not None:
            if glass_point_id in self.focal_points:
                # Suppression du point précédent associé au même id
                previous_canva_point_id = self.focal_points[glass_point_id]['canva_point_id']
                self.canvas.delete(previous_canva_point_id)  # Delete the last point from the canvas
                if previous_canva_point_id in self.canvas_point_ids: # Ensure it's in the list before removing
                    self.canvas_point_ids.remove(previous_canva_point_id)
                
            # Calculate angles (Pass coordinates relative to the new center)
            x_relative_to_center = x_absolute_space - self.center_coords[0]
            y_relative_to_center = y_absolute_space - self.center_coords[1]
            angle_theta = calculate_theta(x_relative_to_center, y_relative_to_center)
            angle_delta = calculate_delta(x_relative_to_center, y_relative_to_center, domain_location_id) # Use location ID for delta

            # Ajout au canvas
            canva_point_id = self.canvas.create_oval(x_canvas-self.point_size, y_canvas-self.point_size, x_canvas+self.point_size, y_canvas+self.point_size, fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[glass_point_id-1]))
            self.canvas_point_ids.append(canva_point_id)  # Store the ID of the created point
            
            # Ajout au dictionnaire self.focal_points, stockant les coordonnées RELATIVES au centre
            self.focal_points[glass_point_id] = {
                'canva_point_id': canva_point_id,
                'canvas_coords': np.array([x_canvas, y_canvas]),
                'abs_space_coords': np.array([x_absolute_space, y_absolute_space]), # Store absolute coords
                'rel_space_coords': np.array([x_relative_to_center, y_relative_to_center]), # Store relative coords
                'angle_theta': angle_theta,
                'angle_delta': angle_delta
            }
            
            # Select the newly added focal point
            self.selected_point_id = canva_point_id
            self.selected_point_type = 'focal'
            self.selected_focal_glass_id = glass_point_id

            # Update la frame de résultats et les trajectoires
            self.setup_strvar.set("")
            self.compute_all_self_attributes()
            self.update_canvas_limit_traj()
            self.update_canvas_normal_traj()
            self.update_results_frame()
            self.update_point_input_fields() # Update input fields for the newly added point and apply outline

    # MODIFIED EXISTING FUNCTION
    def add_initial_point(self, event):
        """
        Adds or updates the initial point on the canvas based on a right-click event.
        Handles domain classification and updates UI.
        """
        x_canvas, y_canvas = event.x, event.y
        # Get absolute space coordinates from canvas click
        x_absolute_space, y_absolute_space = self.get_absolute_space_coords_from_canvas_coords(x_canvas, y_canvas)
        
        # Classify based on absolute location
        domain_id = self.classify_point_per_domain_location(x_absolute_space, y_absolute_space, is_focal_point=False)
        if domain_id is None:
            self.show_notification("Initial point cannot be placed at the center.", bg_color='red')
            return
            
        if self.canvas_initial_point_id is not None:
            # Suppression du point initial précédent
            self.canvas.delete(self.canvas_initial_point_id)  
            
        # Recalculate canvas coords in case of minor snapping to quadrant (though initial point can be on axis)
        x_canvas_final, y_canvas_final = self.get_canvas_coords_from_absolute_space_coords(x_absolute_space, y_absolute_space)

        # Ajout au canvas
        self.canvas_initial_point_id = self.canvas.create_oval(x_canvas_final-self.point_size, y_canvas_final-self.point_size, x_canvas_final+self.point_size, y_canvas_final+self.point_size, fill='black')
        
        # Création du dictionnaire lié, stockant les coordonnées RELATIVES au centre
        self.initial_point = {
            'domain_id': domain_id,
            'canva_point_id': self.canvas_initial_point_id,
            'canvas_coords': np.array([x_canvas_final, y_canvas_final]),
            'abs_space_coords': np.array([x_absolute_space, y_absolute_space]), # Store absolute coords
            'rel_space_coords': np.array([x_absolute_space - self.center_coords[0], y_absolute_space - self.center_coords[1]]) # Store relative coords
        }

        # Select the newly added initial point
        self.selected_point_id = self.canvas_initial_point_id
        self.selected_point_type = 'initial'
        self.selected_focal_glass_id = None
        
        self.setup_strvar.set("")
        # Update la frame de résultats et les trajectoires
        self.update_canvas_normal_traj()
        self.update_results_frame()
        self.update_point_input_fields() # Apply outline

    # MODIFIED EXISTING FUNCTION
    def undo_focal_point(self):
        """
        Removes the last added focal point.
        Updates UI and clears input fields if the undone point was selected.
        """
        if self.canvas_point_ids:
            canva_last_point_id = self.canvas_point_ids.pop()
            self.canvas.delete(canva_last_point_id)  # Delete the last point from the canvas
            glass_last_point_id = self.find_glass_point_id_from_canvas_id(canva_last_point_id)
            if glass_last_point_id in self.focal_points: # Ensure it exists before deleting
                del self.focal_points[glass_last_point_id]
                # If the undone point was selected, deselect it
                if self.selected_point_id == canva_last_point_id:
                    self.unselect_point()
            
            self.setup_strvar.set("")
            # Update la frame de résultats et les trajectoires
            self.compute_all_self_attributes()
            self.update_canvas_limit_traj()
            self.update_canvas_normal_traj()
            self.update_results_frame()
            self.update_point_input_fields() # Update input fields and outline
        else:
            self.show_notification("Warning : no more focal points to undo", bg_color='yellow')

    # MODIFIED EXISTING FUNCTION
    def remove_initial_point(self):
        """
        Removes the initial point from the canvas.
        Updates UI and clears input fields if the initial point was selected.
        """
        if self.canvas_initial_point_id is not None:
            self.canvas.delete(self.canvas_initial_point_id)  # Delete the initial point from the canvas
            self.canvas_initial_point_id = None
            self.initial_point = {}
            # If the removed point was selected, deselect it
            if self.selected_point_type == 'initial':
                self.unselect_point()
            
            self.setup_strvar.set("")
            # Update la frame de résultats et la trajectoire
            self.update_canvas_normal_traj()
            self.update_results_frame()
            self.update_point_input_fields()
        else:
            self.show_notification("Warning : no initial point to remove", bg_color='yellow')
    
    def clear_canvas_points(self):
        """
        Clears all points (focal and initial) from the canvas.
        Resets all point-related data and UI elements.
        """
        # Remove all points from the canvas
        self.canvas.delete("all") # This deletes everything, including lines and grid.
        
        self.canvas_point_ids = []
        self.focal_points = {}
        
        self.canvas_initial_point_id = None
        self.initial_point = {}
        
        self.unselect_point()
        self.setup_strvar.set("")
        self.compute_all_self_attributes()
        self.reload_canvas()
        self.show_notification("All canvas points cleared", bg_color='cyan')
        
        # Update la frame de résultats et les trajectoires
        self.update_results_frame()
        self.update_point_input_fields()
    
    def reset_center(self):
        self.center_x_var.set("0.0")
        self.center_y_var.set("0.0")
        self.update_center_coords()
    
    #%% Setup save handling
    def save_setup(self, new_setup_name, is_base_save=False):
        """
        Save the setup of grid dimensions, center coordinates, focal points coordinates and initial point
        """
        if type(new_setup_name) is str:
            self.setup_name = new_setup_name.strip()
        else:
            self.setup_name = new_setup_name.get().strip()   # Récupération du texte entré
        print("Setup name :", self.setup_name)

        # Vérifier que le nom n'est pas vide
        if not self.setup_name and not is_base_save:
            tk.messagebox.showwarning("Error", "Enter a valid name.")
            return

        # Si le setup name est "base" et ce n'est pas le démarrage, refuser
        if self.setup_name.lower() == "base" and not is_base_save:
            tk.messagebox.showerror("This name is protected", 
                                 'The name "base" is protected. please choose another name.')
            return

        # Chemin du dossier de sauvegarde
        folder = "Saved_setups"
        os.makedirs(folder, exist_ok=True)

        # Chemin complet du fichier
        file_path = os.path.join(folder, f"{self.setup_name}.csv")
        
        if os.path.exists(file_path) and not is_base_save:
            action = ask_overwrite_action(self.setup_name)
        
            if action == "replace":
                pass  # on continue et écrase le fichier
            elif action == "new":
                base_name = self.setup_name
                i = 1
                new_file_path = os.path.join(folder, f"{base_name}_{i}.csv")
                while os.path.exists(new_file_path):
                    i += 1
                    new_file_path = os.path.join(folder, f"{base_name}_{i}.csv")
                
                file_path = new_file_path
                self.setup_name = f"{base_name}_{i}"  # on met à jour le nom
                print(f"New auto-generated : {self.setup_name}")
            else:  # cancel
                return
        
        df = self.format_to_csv_savable()
        df.to_csv(file_path, index=False)

        print(f"Setup '{self.setup_name}' saved in {file_path}")
        self.setup_strvar.set(f"{self.setup_name}")
        # Fermer la fenêtre pop-up (debind toutes les touches liées)
        if not is_base_save:
            self.save_popup.destroy()
    
    def format_to_csv_savable(self):
        # --- Récupération des dimensions de la grille ---
        grid_dim_array = np.array([[self.min_space_x, self.max_space_x],
                                   [self.min_space_y, self.max_space_y]])
        min_x, max_x = grid_dim_array[0]
        min_y, max_y = grid_dim_array[1]
    
        # --- Récupération du centre ---
        center_x, center_y = self.center_coords
    
        # --- Récupération des données des points focaux ---
        L_focal_points = [None] * 4
        for glass_point_id, dict_focal_point in self.focal_points.items():
            focal_point = dict_focal_point['abs_space_coords']
            L_focal_points[glass_point_id-1] = focal_point
    
        focals = []
        for f in L_focal_points:
            if f is None:
                focals.extend([None, None])
            else:
                focals.extend(list(f))
    
        # --- Récupération du point initial ---
        if not self.initial_point:
            init_x, init_y = None, None
        else:
            init_x, init_y = self.initial_point['abs_space_coords']
        
        # --- Construction d'une ligne de données ---
        data = {
            "min_x": min_x, "max_x": max_x,
            "min_y": min_y, "max_y": max_y,
            "center_x": center_x, "center_y": center_y,
            "focal1_x": focals[0], "focal1_y": focals[1],
            "focal2_x": focals[2], "focal2_y": focals[3],
            "focal3_x": focals[4], "focal3_y": focals[5],
            "focal4_x": focals[6], "focal4_y": focals[7],
            "init_x": init_x, "init_y": init_y
        }
        
        df = pd.DataFrame([data])
        
        return(df)
    
    def open_save_popup(self):
        self.save_popup = tk.Toplevel(self.root)
        self.save_popup.title("Save window")
        self.save_popup.geometry("300x150")

        ttk.Label(self.save_popup, text="Enter setup name :").pack(pady=2)

        # Création d'une variable pour stocker le texte
        strvar = tk.StringVar()

        # Champ de saisie (ttk)
        entry = ttk.Entry(self.save_popup, textvariable=strvar)
        entry.pack(fill=tk.X, pady=2)

        # Associer la touche Enter à la validation
        entry.bind("<Return>", lambda event: self.save_setup(strvar))

        # Bouton pour valider la saisie (ttk)
        validate_button = ttk.Button(self.save_popup, text="Validate setup name",
                                     command=lambda: self.save_setup(strvar))
        validate_button.pack()

        # Bouton pour fermer la fenêtre (ttk)
        close_button = ttk.Button(self.save_popup, text="Cancel save", command=self.save_popup.destroy)
        close_button.pack()
    
    
    #%% Apply setup handling
    def find_all_possible_setups(self):
        folder = "Saved_setups"
        if not os.path.exists(folder):
            return ["base"]

        csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        csv_names = [os.path.splitext(os.path.basename(f))[0] for f in csv_files]
        if "base" in csv_names:
            csv_names.remove("base")
        
        # Toujours inclure "base" en premier
        return ["base"] + csv_names

    def update_setup_menu(self, event=None):
        self.setups = self.find_all_possible_setups()

        menu = self.select_setup_menu["menu"]
        menu.delete(0, "end")  # Supprime anciennes options

        # Ajoute les nouvelles options
        for s in self.setups:
            menu.add_command(
                label=s,
                command=lambda value=s: self.apply_new_setup(value)
            )

        # Si la valeur courante n’existe plus → reset sur "base"
        if self.setup_strvar.get() not in self.setups:
            self.setup_strvar.set("base")
    
    def apply_new_setup(self, value):
        self.setup_strvar.set(value)
        print(f"Applying new setup : {value}")
        self.retrieve_setup_and_modify_corresponding_variables(value)
        self.complete_missing_attributes_of_focal_and_initial_points_from_abs()
        
        # Fully redrawing canvas
        self.unselect_point()
        self.compute_all_self_attributes() # Recalculate attributes (rho, r, h1_lim)
        self.reload_canvas()
        self.update_center_input_fields()
        self.update_dimensions_input_fields()
        self.update_point_input_fields() # Update input fields for selected point and apply outline
        self.update_results_frame() # Update results frame
    
    def retrieve_setup_and_modify_corresponding_variables(self, setup_name):
        """
        Load a setup from a CSV file and update the corresponding object variables.
        """
        folder = "Saved_setups"
        file_path = os.path.join(folder, setup_name + ".csv")
    
        if not os.path.exists(file_path):
            print(f"The file {file_path} does not exist.")
            return
    
        # Read the CSV (only one row expected)
        df = pd.read_csv(file_path)
        row = df.iloc[0]
    
        # --- Update grid dimensions ---
        self.min_space_x = row["min_x"]
        self.max_space_x = row["max_x"]
        self.min_space_y = row["min_y"]
        self.max_space_y = row["max_y"]
        
        # --- Update center coordinates ---
        self.center_coords = np.array([row["center_x"], row["center_y"]])
    
        # --- Update focal points ---
        self.focal_points = {}
        for i in range(4):  # focal1 → focal4
            x = row[f"focal{i+1}_x"]
            y = row[f"focal{i+1}_y"]
            if pd.notna(x) and pd.notna(y):  # the point exists
                self.focal_points[i+1] = {"abs_space_coords": np.array([x, y]),
                                          "rel_space_coords": np.array([x - row["center_x"], y - row["center_y"]])}
    
        # --- Update initial point ---
        if pd.isna(row["init_x"]) or pd.isna(row["init_y"]):
            self.initial_point = None
        else:
            self.initial_point = {"abs_space_coords": np.array([row["init_x"], row["init_y"]]),
                                  "rel_space_coords": np.array([row["init_x"] - row["center_x"], row["init_y"] - row["center_y"]])}
    
        print(f"Setup '{setup_name}' successfully loaded.")
    
    def complete_missing_attributes_of_focal_and_initial_points_from_abs(self):
        # Complete focal points informations (except canvas ones)
        for glass_point_id in self.focal_points.keys():
            abs_coords = self.focal_points[glass_point_id]["abs_space_coords"]
            center_coords = self.center_coords
            rel_coords = abs_coords - center_coords
            
            domain_location_id = self.classify_point_per_domain_location(abs_coords[0], abs_coords[1])
            self.focal_points[glass_point_id]["rel_space_coords"] = rel_coords
            self.focal_points[glass_point_id]["angle_theta"] = calculate_theta(rel_coords[0], rel_coords[1]) # Use relative for angle calculation
            self.focal_points[glass_point_id]["angle_delta"] = calculate_delta(rel_coords[0], rel_coords[1], domain_location_id) # Use relative for angle calculation
        
        # Complete initial point informations (except canvas ones)
        if self.initial_point:
            abs_coords_init = self.initial_point["abs_space_coords"]
            rel_coords_init = abs_coords_init - self.center_coords
            self.initial_point["rel_space_coords"] = rel_coords_init
            self.initial_point['domain_id'] = self.classify_point_per_domain_location(abs_coords_init[0], abs_coords_init[1])
            
    def update_center_input_fields(self):
        self.center_x_var.set(f"{self.center_coords[0]:.2f}")
        self.center_y_var.set(f"{self.center_coords[1]:.2f}")
    
    def update_dimensions_input_fields(self):
        self.min_space_x_var.set(f"{self.min_space_x:.1f}")
        self.max_space_x_var.set(f"{self.max_space_x:.1f}")
        self.min_space_y_var.set(f"{self.min_space_y:.1f}")
        self.max_space_y_var.set(f"{self.max_space_y:.1f}")

    #%%Calculus linked functions
    # Ces fonctions opèrent sur les space_coords qui sont maintenant relatives au centre
    def compute_rho(self):
        assert len(self.focal_points) == 4 
        
        a1, b1 = self.focal_points[1]['rel_space_coords'] 
        a2, b2 = self.focal_points[2]['rel_space_coords'] 
        a3, b3 = self.focal_points[3]['rel_space_coords'] 
        a4, b4 = self.focal_points[4]['rel_space_coords'] 
        
        self.rho = a4*b3*a2*b1 / (b4*a3*b2*a1) 
    
    def compute_r(self):
        assert len(self.focal_points) == 4
        
        a1, b1 = self.focal_points[1]['rel_space_coords'] 
        a2, b2 = self.focal_points[2]['rel_space_coords'] 
        a3, b3 = self.focal_points[3]['rel_space_coords'] 
        a4, b4 = self.focal_points[4]['rel_space_coords'] 
        
        self.r = -1/a1 + b1 / (a1*b2) - b1*a2 / (a1*b2*a3) + b1*a2*b3 / (a1*b2*a3*b4) 
    
    def compute_limit_h1_rel(self):
        assert len(self.focal_points) == 4
        
        if self.rho <= 1: 
            self.h1_lim = 0 
        else: 
            self.h1_lim = (self.rho - 1) / self.r
    
    def compute_lim_trajs_lengths_per_zones(self):
        dist1 = np.linalg.norm(self.intersect_point1 - self.start_limit_point)
        dist2 = np.linalg.norm(self.intersect_point2 - self.intersect_point1)
        dist3 = np.linalg.norm(self.intersect_point3 - self.intersect_point2)
        dist4 = np.linalg.norm(self.start_limit_point - self.intersect_point3)
        
        dist_total = dist1 + dist2 + dist3 + dist4
        
        return(dist1, dist2, dist3, dist4, dist_total)
        
    def compute_lim_trajs_durations_per_zones(self):
        time1 = np.log((self.start_limit_point[0] - self.focal_points[1]['rel_space_coords'][0]) / (self.intersect_point1[0] - self.focal_points[1]['rel_space_coords'][0])) * 1 / self.gamma
        time2 = np.log((self.intersect_point1[0] - self.focal_points[2]['rel_space_coords'][0]) / (self.intersect_point2[0] - self.focal_points[2]['rel_space_coords'][0])) * 1 / self.gamma
        time3 = np.log((self.intersect_point2[0] - self.focal_points[3]['rel_space_coords'][0]) / (self.intersect_point3[0] - self.focal_points[3]['rel_space_coords'][0])) * 1 / self.gamma
        time4 = np.log((self.intersect_point3[0] - self.focal_points[4]['rel_space_coords'][0]) / (self.start_limit_point[0] - self.focal_points[4]['rel_space_coords'][0])) * 1 / self.gamma
        
        time_total = time1 + time2 + time3 + time4
        
        return(time1, time2, time3, time4, time_total)
    
    def compute_lim_trajs_amplitudes(self):
        amp_x = np.linalg.norm(self.intersect_point2 - self.start_limit_point)
        amp_y = np.linalg.norm(self.intersect_point3 - self.intersect_point1)
        
        return(amp_x, amp_y)
        
    
    def compute_all_self_attributes(self):
        """
        Calls all necessary computation functions (rho, r, h1_lim) if four focal points are present.
        Includes error handling for computations.
        """
        if len(self.focal_points) == 4:
            try:
                self.compute_rho()
                self.compute_r()
                self.compute_limit_h1_rel()
            except ZeroDivisionError:
                self.show_notification("Cannot compute rho, r, or h1_lim due to division by zero. Adjust focal points.", bg_color='red')
                self.rho = float('nan')
                self.r = float('nan')
                self.h1_lim = float('nan')
            except Exception as e:
                self.show_notification(f"Error computing attributes: {e}", bg_color='red')
                self.rho = float('nan')
                self.r = float('nan')
                self.h1_lim = float('nan')
        else:
            self.rho = float('nan')
            self.r = float('nan')
            self.h1_lim = float('nan')

    #%% Update interface functions
    def update_results_frame(self):
        """
        Updates the text in the results frame with current point coordinates,
        and calculated parameters (rho, r, h1_lim, trajectory lengths and durations).
        """
        results_text = ""
        if not self.focal_points and not self.initial_point:
            results_text += "No points placed."
        
        if self.initial_point or self.focal_points:
            
            results_text += "Coordonnées des points (absolues)\n"
        if self.initial_point:
            x_space_abs, y_space_abs = self.initial_point['abs_space_coords']
            results_text += f"Point initial : ({x_space_abs:.2f}, {y_space_abs:.2f})\n\n"
        
        if self.focal_points:
            for point_id in sorted(self.focal_points):
                point_data = self.focal_points[point_id]
                x_space_abs, y_space_abs = point_data['abs_space_coords']
                results_text += f"Point focal {point_id} : ({x_space_abs:.2f}, {y_space_abs:.2f})"
                
                if 'angle_theta' in point_data and 'angle_delta' in point_data:
                    results_text += f" (Theta: {point_data['angle_theta']:.2f}°, Delta: {point_data['angle_delta']:.2f}°)\n"
                else:
                    results_text += "\n"
            
            if len(self.focal_points) == 4:
                results_text += "\n\nGrandeurs caractéristiques\n"
                results_text += f"rho : {self.rho:.4f}\n"
                results_text += f"r : {self.r:.4f}\n"
                h1_lim_abs = self.h1_lim + self.center_coords[0]
                results_text += f"h1_lim : {h1_lim_abs:.4f}\n"
                
                if self.rho > 1 and not np.isnan(self.rho) and not np.isinf(self.rho): # Check for valid rho
                    results_text += "\n\nCaractéristiques de l'orbite périodique\n"
                    try:
                        dist1, dist2, dist3, dist4, dist_total = self.compute_lim_trajs_lengths_per_zones()
                        time1, time2, time3, time4, time_total = self.compute_lim_trajs_durations_per_zones()
                        amp_x, amp_y = self.compute_lim_trajs_amplitudes()
                        results_text += f"Trajectoire domaine 1 :\n Longueur : {dist1:.2f}, Durée : {time1:.2f} h\n\n"
                        results_text += f"Trajectoire domaine 2 :\n Longueur : {dist2:.2f}, Durée : {time2:.2f} h\n\n"
                        results_text += f"Trajectoire domaine 3 :\n Longueur : {dist3:.2f}, Durée : {time3:.2f} h\n\n"
                        results_text += f"Trajectoire domaine 4 :\n Longueur : {dist4:.2f}, Durée : {time4:.2f} h\n\n"
                        results_text += f"Trajectoire complète :\n Longueur totale : {dist_total:.2f}, Durée totale : {time_total:.4f} h\n\n"
                        results_text += "\nAmplitudes\n"
                        results_text += f"Amplitude selon x : {amp_x:.4f}, Amplitude selon y : {amp_y:.4f}"
                        results_text += "\n\nCoordonnées des points d'intersections\n"
                        start_limit_point_abs = self.start_limit_point + self.center_coords
                        intersect_point1_abs = self.intersect_point1 + self.center_coords
                        intersect_point2_abs = self.intersect_point2 + self.center_coords
                        intersect_point3_abs = self.intersect_point3 + self.center_coords
                        results_text += f"Point d'intersection 4-1 : ({start_limit_point_abs[0]:.2f}, {start_limit_point_abs[1]:.2f})\n"
                        results_text += f"Point d'intersection 1-2 : ({intersect_point1_abs[0]:.2f}, {intersect_point1_abs[1]:.2f})\n"
                        results_text += f"Point d'intersection 2-3 : ({intersect_point2_abs[0]:.2f}, {intersect_point2_abs[1]:.2f})\n"
                        results_text += f"Point d'intersection 3-4 : ({intersect_point3_abs[0]:.2f}, {intersect_point3_abs[1]:.2f})\n"
                    except Exception as e:
                        results_text += f"Error calculating trajectories: {e}\n"
                        results_text += "Please ensure focal points are not on axes relative to each other for trajectory calculations."
                else:
                    results_text += "\n Pas d'orbite périodique \n"
            
        self.results_label.config(text=results_text)

    #%% Update canvas functions
    def draw_line_with_axis_cut(self, point1_space_relative, point2_space_relative, axis, storage_canvas_id_list, line_color="black", line_width=2, with_dashed_line=True):
        """
        Draws a line between two points (in space coordinates relative to the center) and handles axis crossing.
        Returns the intersection point in space coordinates relative to the center.
        Includes robust checks for axis crossing.
        """
        x1_space_relative, y1_space_relative = point1_space_relative
        x2_space_relative, y2_space_relative = point2_space_relative
        
        x_intersect_space_relative = 0
        y_intersect_space_relative = 0

        epsilon_axis_check = 1e-9 # Tolerance for checking if a point is on an axis or if line crosses

        if axis == 'x=0':
            # Check if the line actually crosses the x=0 axis (relative to center)
            # It crosses if the x-coordinates have different signs (or one is zero and the other is not)
            if (x1_space_relative < -epsilon_axis_check and x2_space_relative > epsilon_axis_check) or \
               (x1_space_relative > epsilon_axis_check and x2_space_relative < -epsilon_axis_check) or \
               (abs(x1_space_relative) < epsilon_axis_check and abs(x2_space_relative) > epsilon_axis_check) or \
               (abs(x2_space_relative) < epsilon_axis_check and abs(x1_space_relative) > epsilon_axis_check):
                
                # Avoid division by zero if x1 and x2 are very close
                if abs(x2_space_relative - x1_space_relative) < epsilon_axis_check:
                    # If points are vertically aligned, no unique intersection with x=0 unless they are both on it
                    if abs(x1_space_relative) < epsilon_axis_check: # Both on x=0
                        x_intersect_space_relative = 0
                        y_intersect_space_relative = y1_space_relative # Or y2, or midpoint
                    else: # Parallel to x=0 and not on it, no intersection
                        return np.array([x2_space_relative, y2_space_relative]) # No cut, just draw the full segment
                else:
                    t = -x1_space_relative / (x2_space_relative - x1_space_relative)
                    x_intersect_space_relative = 0 
                    y_intersect_space_relative = y1_space_relative + t * (y2_space_relative - y1_space_relative)
            else: # Line does not cross, or is parallel to the axis and not on it
                return np.array([x2_space_relative, y2_space_relative]) # No cut, just draw the full segment
        elif axis == 'y=0':
            # Check if the line actually crosses the y=0 axis (relative to center)
            if (y1_space_relative < -epsilon_axis_check and y2_space_relative > epsilon_axis_check) or \
               (y1_space_relative > epsilon_axis_check and y2_space_relative < -epsilon_axis_check) or \
               (abs(y1_space_relative) < epsilon_axis_check and abs(y2_space_relative) > epsilon_axis_check) or \
               (abs(y2_space_relative) < epsilon_axis_check and abs(y1_space_relative) > epsilon_axis_check):

                if abs(y2_space_relative - y1_space_relative) < epsilon_axis_check:
                    if abs(y1_space_relative) < epsilon_axis_check: # Both on y=0
                        y_intersect_space_relative = 0
                        x_intersect_space_relative = x1_space_relative # Or x2, or midpoint
                    else: # Parallel to y=0 and not on it, no intersection
                        return np.array([x2_space_relative, y2_space_relative]) # No cut, just draw the full segment
                else:
                    t = -y1_space_relative / (y2_space_relative - y1_space_relative)
                    x_intersect_space_relative = x1_space_relative + t * (x2_space_relative - x1_space_relative)
                    y_intersect_space_relative = 0 
            else: # Line does not cross, or is parallel to the axis and not on it
                return np.array([x2_space_relative, y2_space_relative]) # No cut, just draw the full segment
        else:
            raise ValueError(f"Invalid axis name: '{axis}'. Expected 'x=0' or 'y=0'.")
        
        # Convert relative coordinates to absolute coordinates for drawing on canvas
        x1_absolute = x1_space_relative + self.center_coords[0]
        y1_absolute = y1_space_relative + self.center_coords[1]
        x2_absolute = x2_space_relative + self.center_coords[0]
        y2_absolute = y2_space_relative + self.center_coords[1]
        x_intersect_absolute = x_intersect_space_relative + self.center_coords[0]
        y_intersect_absolute = y_intersect_space_relative + self.center_coords[1]

        # Transform to canvas coordinates
        x1_canvas, y1_canvas = self.get_canvas_coords_from_absolute_space_coords(x1_absolute, y1_absolute)
        x2_canvas, y2_canvas = self.get_canvas_coords_from_absolute_space_coords(x2_absolute, y2_absolute)
        x_intersect_canvas, y_intersect_canvas = self.get_canvas_coords_from_absolute_space_coords(x_intersect_absolute, y_intersect_absolute)
        
        # Draw the 1st part (before the axis) as continuous
        canvas_line_id = self.canvas.create_line(x1_canvas, y1_canvas, x_intersect_canvas, y_intersect_canvas, fill=line_color, width=line_width)
        storage_canvas_id_list.append(canvas_line_id)
        
        if with_dashed_line:
            # Draw the 2nd part (after the axis) as dashed
            canvas_line_id = self.canvas.create_line(x_intersect_canvas, y_intersect_canvas, x2_canvas, y2_canvas, fill=line_color, width=line_width, dash=(4, 8))
            storage_canvas_id_list.append(canvas_line_id)
        
        return np.array([x_intersect_space_relative, y_intersect_space_relative]) # Return the intersection point in relative coordinates
    
    def update_canvas_limit_traj(self, with_dashed_line=False):
        """
        Draws the limit trajectory (if a periodic orbit exists).
        Clears previous limit trajectories before redrawing.
        """
        # Clear all limit trajectories
        for canvas_line_id in self.canvas_lim_line_ids:
            self.canvas.delete(canvas_line_id)
        self.canvas_lim_line_ids = []
        
        # Only draw if 4 focal points exist and rho indicates a periodic orbit (and rho is a valid number)
        if len(self.focal_points) == 4 and self.rho > 1 and not np.isnan(self.rho) and not np.isinf(self.rho):
            try:
                # start_limit_point is now relative to center
                self.start_limit_point = np.array([self.h1_lim, 0]) 
                
                # Traj 1 (from h1_lim to focal point 1, crossing x=0)
                point1_traj1, point2_traj1 = self.start_limit_point, self.focal_points[1]['rel_space_coords']
                self.intersect_point1 = self.draw_line_with_axis_cut(point1_traj1, point2_traj1, 'x=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Traj 2 (from intersect_point1 to focal point 2, crossing y=0)
                point1_traj2, point2_traj2 = self.intersect_point1, self.focal_points[2]['rel_space_coords']
                self.intersect_point2 = self.draw_line_with_axis_cut(point1_traj2, point2_traj2, 'y=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Traj 3 (from intersect_point2 to focal point 3, crossing x=0)
                point1_traj3, point2_traj3 = self.intersect_point2, self.focal_points[3]['rel_space_coords']
                self.intersect_point3 = self.draw_line_with_axis_cut(point1_traj3, point2_traj3, 'x=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Traj 4 (from intersect_point3 to focal point 4, crossing y=0)
                point1_traj4, point2_traj4 = self.intersect_point3, self.focal_points[4]['rel_space_coords']
                intersect_point4 = self.draw_line_with_axis_cut(point1_traj4, point2_traj4, 'y=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Check if the trajectory closes back to the start_limit_point (with a small tolerance)
                if np.linalg.norm(self.start_limit_point - intersect_point4) >= 1e-8: # Increased tolerance slightly for floating point arithmetic
                    self.show_notification('Problem in calculation or low precision for limit trajectory closing.', bg_color='orange')
            except Exception as e:
                self.show_notification(f"Error drawing limit trajectory: {e}", bg_color='red')

    def update_canvas_normal_traj(self, nb_iter=20, with_dashed_line=True):
        """
        Draws the normal trajectory starting from the initial point.
        Clears previous normal trajectories before redrawing.
        """
        # Clear all trajectories
        for canvas_line_id in self.canvas_norm_line_ids:
            self.canvas.delete(canvas_line_id)
        self.canvas_norm_line_ids = []
        
        # Only draw if 4 focal points exist and an initial point is placed
        if len(self.focal_points) == 4 and self.initial_point:
            try:
                # Retrieve the domain id of the initial point
                glass_point_id = self.initial_point['domain_id']
                
                # Initialize points for the first trajectory, and the axis variable
                # The space_coords are already relative to the center
                point1_traj, point2_traj = self.initial_point['rel_space_coords'], self.focal_points[glass_point_id]['rel_space_coords']
                if glass_point_id == 1 or glass_point_id == 3: 
                    axis = 'x=0' 
                else: 
                    axis = 'y=0' 
                
                for i in range(nb_iter): 
                    # Draw and calculate the first intersection point (relative coordinates)
                    intersect_point = self.draw_line_with_axis_cut(point1_traj, point2_traj, axis, self.canvas_norm_line_ids, line_color=self.color_norm_lines, line_width=self.line_width_norm, with_dashed_line=with_dashed_line)
                    
                    # Update variables for the next iteration
                    glass_point_id = glass_point_id % 4 + 1 # Cycle through focal points (1->2, 2->3, 3->4, 4->1)
                    point1_traj, point2_traj = intersect_point, self.focal_points[glass_point_id]['rel_space_coords'] 
                    axis = switch_axis(axis) # Alternate axis (x=0 -> y=0, y=0 -> x=0)
            except Exception as e:
                self.show_notification(f"Error drawing normal trajectory: {e}", bg_color='red')

    def reload_canvas(self, event=None):
        self._draw_grid_and_axes()
        self.redraw_all_points_and_trajectories()
    
    def redraw_all_points_and_trajectories(self):
        """
        Redraws all focal points and the initial point on the canvas.
        This function should be called after canvas resize, center change, or point
        creation/deletion/application of input coordinates, but NOT during continuous dragging.
        It does NOT handle the visual feedback for the currently selected point (that's update_point_input_fields' job).
        """
        # Clear existing points from the canvas
        current_canvas_point_ids = list(self.canvas_point_ids) # Copy before modifying
        for canva_id in current_canvas_point_ids:
            self.canvas.delete(canva_id)
            if canva_id in self.canvas_point_ids: # Ensure it's still in the list before removing
                 self.canvas_point_ids.remove(canva_id) # Remove from internal list as well
        if self.canvas_initial_point_id:
            self.canvas.delete(self.canvas_initial_point_id)
            self.canvas_initial_point_id = None # Reset ID after deletion

        # Clear trajectory lines (they will be redrawn by update_canvas_limit_traj/normal_traj)
        for line_id in self.canvas_lim_line_ids:
            self.canvas.delete(line_id)
        self.canvas_lim_line_ids = []
        for line_id in self.canvas_norm_line_ids:
            self.canvas.delete(line_id)
        self.canvas_norm_line_ids = []

        # Redraw focal points
        for glass_point_id in sorted(self.focal_points.keys()):
            point_data = self.focal_points[glass_point_id]
            # Coordinates are stored relative to center, convert to absolute for drawing
            x_space_relative, y_space_relative = point_data['rel_space_coords']
            x_absolute_space = x_space_relative + self.center_coords[0]
            y_absolute_space = y_space_relative + self.center_coords[1]

            x_canvas, y_canvas = self.get_canvas_coords_from_absolute_space_coords(x_absolute_space, y_absolute_space)
            
            canva_point_id = self.canvas.create_oval(
                x_canvas - self.point_size, y_canvas - self.point_size,
                x_canvas + self.point_size, y_canvas + self.point_size,
                fill=rgb_float_tuple_to_hex(self.focal_points_colors_RGB[glass_point_id - 1]),
                outline="black", width=1 # Outline will be handled by update_point_input_fields
            )
            self.canvas_point_ids.append(canva_point_id)
            point_data['canva_point_id'] = canva_point_id # Update stored canvas ID
            point_data['canvas_coords'] = np.array([x_canvas, y_canvas])

        # Redraw initial point
        if self.initial_point:
            x_space_relative, y_space_relative = self.initial_point['rel_space_coords']
            x_absolute_space = x_space_relative + self.center_coords[0]
            y_absolute_space = y_space_relative + self.center_coords[1]

            x_canvas, y_canvas = self.get_canvas_coords_from_absolute_space_coords(x_absolute_space, y_absolute_space)

            self.canvas_initial_point_id = self.canvas.create_oval(
                x_canvas - self.point_size, y_canvas - self.point_size,
                x_canvas + self.point_size, y_canvas + self.point_size,
                fill='black',
                outline="black", width=1 # Outline will be handled by update_point_input_fields
            )
            self.initial_point['canva_point_id'] = self.canvas_initial_point_id
            self.initial_point['canvas_coords'] = np.array([x_canvas, y_canvas])

        
        self.update_canvas_limit_traj()
        self.update_canvas_normal_traj()
    
    #%% Functions to handle the center input frame
    def create_center_input_frame(self):
        """Creates a dedicated section in the middle panel for grid dimensions input fields."""
        self.center_input_frame = ttk.LabelFrame(self.middle_frame, text="Center coordinates", padding=10)
        self.center_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.center_input_frame, text="Center X:").pack(pady=2)
        self.center_x_var = tk.StringVar(value=f"{self.center_coords[0]:.2f}")
        self.center_x_entry = ttk.Entry(self.center_input_frame, textvariable=self.center_x_var)
        self.center_x_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.center_input_frame, text="Center Y:").pack(pady=2)
        self.center_y_var = tk.StringVar(value=f"{self.center_coords[1]:.2f}")
        self.center_y_entry = ttk.Entry(self.center_input_frame, textvariable=self.center_y_var)
        self.center_y_entry.pack(fill=tk.X, pady=2)
        
        self.apply_center_coords_button = ttk.Button(self.center_input_frame, text="Apply Center Coordinates", command=self.update_center_coords)
        self.apply_center_coords_button.pack(fill=tk.X, pady=5)
        
        self.reset_center_button = ttk.Button(self.center_input_frame, text="Reset Center to (0,0)", command=self.reset_center)
        self.reset_center_button.pack(fill=tk.X, pady=2)
        
        # Register this frame
        self.register_return_binding(self.center_input_frame, self.update_center_coords)
    
    def update_center_coords(self, *args):
        """
        Updates the center coordinates of the oscillation system. When the center moves, relative coordinates don't.
        Adjusts all existing point's absolute coordinates and redraws the canvas.
        """
        try:
            new_cx = float(self.center_x_var.get())
            new_cy = float(self.center_y_var.get())
    
            # Calculate relative shift
            dx = new_cx - self.center_coords[0]
            dy = new_cy - self.center_coords[1]
    
            # Build a temporary copy of focal points with updated potential coords
            potential_focal_points = {}
            for pid, pdata in self.focal_points.items():
                new_coords = np.array([
                    pdata['rel_space_coords'][0] - dx,
                    pdata['rel_space_coords'][1] - dy
                ])
                potential_focal_points[pid] = {
                    **pdata,
                    "rel_space_coords": new_coords
                }
    
            # Also handle initial_point if needed (optional depending on your logic)
            potential_initial_point = None
            if self.initial_point:
                potential_initial_point = {
                    **self.initial_point,
                    "rel_space_coords": np.array([
                        self.initial_point['rel_space_coords'][0] - dx,
                        self.initial_point['rel_space_coords'][1] - dy
                    ])
                }
    
            # Vérifier les points invalides AVANT modification
            invalid_ids = self.check_invalid_focal_points(potential_focal_points)
    
            if invalid_ids:
                msg = (
                    "Warning: The following focal points will become invalid with the new center "
                    f"and will be removed:\n\n{', '.join(map(str, invalid_ids))}\n\n"
                    "Do you want to continue?"
                )
                proceed = tk.messagebox.askokcancel("Invalid focal points", msg, icon="warning")
    
                if not proceed:
                    self.update_center_input_fields()
                    return  # stop without applying anything
    
            # ---- APPLY ONLY IF USER ACCEPTED ----
            self.center_coords = np.array([new_cx, new_cy])
            self.focal_points = {
                pid: pdata
                for pid, pdata in potential_focal_points.items()
                if pid not in invalid_ids
            }
            if potential_initial_point:
                self.initial_point = potential_initial_point
    
            # Suite du workflow
            self.setup_strvar.set("")
            self.unselect_point()
            self.compute_all_self_attributes()
            self.reload_canvas()
            self.update_results_frame()
            self.update_point_input_fields()
    
        except ValueError:
            self.show_notification("Invalid center coordinates. Please enter numbers.", bg_color='orange')
    
    def check_invalid_focal_points(self, focal_points_dict):
        lst_invalid = []
        for glass_point_id, focal_point_dict in focal_points_dict.items():
            x, y = focal_point_dict['rel_space_coords']
            if glass_point_id == 1 and (x >= 0 or y <= 0):
                lst_invalid.append(glass_point_id)
            if glass_point_id == 2 and (x >= 0 or y >= 0):
                lst_invalid.append(glass_point_id)
            if glass_point_id == 3 and (x <= 0 or y >= 0):
                lst_invalid.append(glass_point_id)
            if glass_point_id == 4 and (x <= 0 or y <= 0):
                lst_invalid.append(glass_point_id)
        return lst_invalid

    #%% Functions to handle the dimensions input frame
    def create_dimensions_input_frame(self):
        """Creates a dedicated section in the middle panel for grid dimensions input fields."""
        self.dimensions_input_frame = ttk.LabelFrame(self.middle_frame, text="Grid dimensions", padding=10)
        self.dimensions_input_frame.pack(fill=tk.X, padx=5, pady=5)
    
        ttk.Label(self.dimensions_input_frame, text="X Min:").pack(pady=2)
        self.min_space_x_var = tk.StringVar(value=f"{self.min_space_x:.1f}") 
        self.min_space_x_entry = ttk.Entry(self.dimensions_input_frame, textvariable=self.min_space_x_var)
        self.min_space_x_entry.pack(fill=tk.X, pady=2)
    
        ttk.Label(self.dimensions_input_frame, text="X Max:").pack(pady=2)
        self.max_space_x_var = tk.StringVar(value=f"{self.max_space_x:.1f}")
        self.max_space_x_entry = ttk.Entry(self.dimensions_input_frame, textvariable=self.max_space_x_var)
        self.max_space_x_entry.pack(fill=tk.X, pady=2)
    
        ttk.Label(self.dimensions_input_frame, text="Y Min:").pack(pady=2)
        self.min_space_y_var = tk.StringVar(value=f"{self.min_space_x:.1f}")
        self.min_space_y_entry = ttk.Entry(self.dimensions_input_frame, textvariable=self.min_space_y_var)
        self.min_space_y_entry.pack(fill=tk.X, pady=2)
    
        ttk.Label(self.dimensions_input_frame, text="Y Max:").pack(pady=2)
        self.max_space_y_var = tk.StringVar(value=f"{self.max_space_y:.1f}")
        self.max_space_y_entry = ttk.Entry(self.dimensions_input_frame, textvariable=self.max_space_y_var)
        self.max_space_y_entry.pack(fill=tk.X, pady=2)
    
        self.apply_dimensions_button = ttk.Button(self.dimensions_input_frame, text="Apply Dimensions", command=self.update_canvas_limits)
        self.apply_dimensions_button.pack(fill=tk.X, pady=5)
        
        # Register this frame
        self.register_return_binding(self.dimensions_input_frame, self.update_canvas_limits)
    
    def update_canvas_limits(self, *args):
        """
        Updates the canvas display limits based on user input.
        Validates input and redraws the canvas.
        """
        try:
            new_min_x = float(self.min_space_x_var.get())
            new_max_x = float(self.max_space_x_var.get())
            new_min_y = float(self.min_space_y_var.get())
            new_max_y = float(self.max_space_y_var.get())

            # Basic validation: max must be greater than min
            if new_max_x <= new_min_x or new_max_y <= new_min_y:
                self.show_notification("Max limit must be greater than Min limit.", bg_color='orange')
                # Revert to previous valid values or handle as appropriate
                self.min_space_x_var.set(str(self.min_space_x))
                self.max_space_x_var.set(str(self.max_space_x))
                self.min_space_y_var.set(str(self.min_space_y))
                self.max_space_y_var.set(str(self.max_space_y))
                return

            self.min_space_x = new_min_x
            self.max_space_x = new_max_x
            self.min_space_y = new_min_y
            self.max_space_y = new_max_y
            
            self.setup_strvar.set("")
            self.unselect_point()
            self.compute_all_self_attributes()
            self.reload_canvas()
            self.update_results_frame()
            self.update_point_input_fields() # Refresh fields after canvas redraw and apply outline
        except ValueError:
            self.show_notification("Invalid limit coordinates. Please enter numbers.", bg_color='orange')

    #%% Functions to handle the point input frame
    def create_point_input_frame(self):
        """Creates a dedicated section in the middle panel for point input fields."""
        self.point_input_frame = ttk.LabelFrame(self.middle_frame, text="Point Coordinates (absolute)", padding=10)
        self.point_input_frame.pack(fill=tk.X, padx=5, pady=5)
    
        ttk.Label(self.point_input_frame, text="Selected Point:").pack(pady=2)
        self.selected_point_label = ttk.Label(self.point_input_frame, text="None")
        self.selected_point_label.pack(pady=2)
    
        ttk.Label(self.point_input_frame, text="X Coordinate:").pack(pady=2)
        self.point_x_var = tk.StringVar(value="")
        self.point_x_entry = ttk.Entry(self.point_input_frame, textvariable=self.point_x_var)
        self.point_x_entry.pack(fill=tk.X, pady=2)
    
        ttk.Label(self.point_input_frame, text="Y Coordinate:").pack(pady=2)
        self.point_y_var = tk.StringVar(value="")
        self.point_y_entry = ttk.Entry(self.point_input_frame, textvariable=self.point_y_var)
        self.point_y_entry.pack(fill=tk.X, pady=2)
        
        self.apply_point_coords_button = ttk.Button(self.point_input_frame, text="Apply Point Coordinates", command=self.apply_point_coordinates)
        self.apply_point_coords_button.pack(fill=tk.X, pady=5)
        self.apply_point_coords_button.pack(fill=tk.X, pady=5)
        
        # Register this frame
        self.register_return_binding(self.point_input_frame, self.apply_point_coordinates)
        
        # Disable fields initially
        self.point_x_entry.config(state='disabled')
        self.point_y_entry.config(state='disabled')
        self.apply_point_coords_button.config(state='disabled')
    
    def update_point_input_fields(self):
        """
        Populates the input fields with the coordinates of the currently selected point
        and manages the enabled/disabled state of the input widgets.
        Also updates the visual selection (blue outline) on the canvas *without* redrawing all points.
        Input/output coordinates are now absolute instead of relative.
        """
        # First, remove selection visual from ALL points
        # Iterate through all focal points' canvas IDs
        for glass_id, point_data in self.focal_points.items():
            if 'canva_point_id' in point_data and point_data['canva_point_id'] is not None:
                self.canvas.itemconfig(point_data['canva_point_id'], outline="black", width=1)
        # Check initial point if it exists
        if self.canvas_initial_point_id is not None:
            self.canvas.itemconfig(self.canvas_initial_point_id, outline="black", width=1)


        if self.selected_point_id is None:
            self.selected_point_label.config(text="None")
            self.point_x_var.set("")
            self.point_y_var.set("")
            self.point_x_entry.config(state='disabled')
            self.point_y_entry.config(state='disabled')
            self.apply_point_coords_button.config(state='disabled')
            return

        self.point_x_entry.config(state='normal')
        self.point_y_entry.config(state='normal')
        self.apply_point_coords_button.config(state='normal')

        # Apply selection visual to the selected point
        if self.selected_point_id is not None:
            self.canvas.itemconfig(self.selected_point_id, outline="blue", width=3)


        if self.selected_point_type == 'initial' and self.initial_point:
            x, y = self.initial_point['abs_space_coords'] # Use absolute coordinates
            self.selected_point_label.config(text="Initial Point")
            self.point_x_var.set(f"{x:.2f}")
            self.point_y_var.set(f"{y:.2f}")
        elif self.selected_point_type == 'focal' and self.selected_focal_glass_id in self.focal_points:
            x, y = self.focal_points[self.selected_focal_glass_id]['abs_space_coords'] # Use absolute coordinates
            self.selected_point_label.config(text=f"Focal Point {self.selected_focal_glass_id}")
            self.point_x_var.set(f"{x:.2f}")
            self.point_y_var.set(f"{y:.2f}")
        else:
            self.unselect_point()
            # If selected point data is somehow invalid, reset selection
            self.update_point_input_fields() # Recurse to reset fields (this will now be safe)
    
    def unselect_point(self):
        self.selected_point_id = None
        self.selected_point_type = None
        self.selected_focal_glass_id = None
    
    def apply_point_coordinates(self):
        """
        Applies the coordinates entered in the input fields to the currently selected point.
        Performs validation and updates the canvas and calculations.
        Input coordinates are now absolute instead of relative.
        """
        if self.selected_point_id is None:
            self.show_notification("No point selected to apply coordinates.", bg_color='orange')
            return

        try:
            new_x_absolute = float(self.point_x_var.get()) # Read as absolute
            new_y_absolute = float(self.point_y_var.get()) # Read as absolute
        except ValueError:
            self.show_notification("Invalid coordinates. Please enter numbers.", bg_color='orange')
            return
        
        # Calculate relative coordinates from absolute and center
        new_x_relative = new_x_absolute - self.center_coords[0]
        new_y_relative = new_y_absolute - self.center_coords[1]

        if self.selected_point_type == 'initial':
            domain_id = self.classify_point_per_domain_location(new_x_absolute, new_y_absolute, is_focal_point=False)
            if domain_id is None:
                self.show_notification("Initial point cannot be placed at the center.", bg_color='red')
                # Revert input fields to previous valid values
                x_prev, y_prev = self.initial_point['abs_space_coords'] # Revert to absolute
                self.point_x_var.set(f"{x_prev:.2f}")
                self.point_y_var.set(f"{y_prev:.2f}")
                return
             
            # Update the initial point data
            self.initial_point['abs_space_coords'] = np.array([new_x_absolute, new_y_absolute])
            self.initial_point['rel_space_coords'] = np.array([new_x_relative, new_y_relative]) # Update relative too
            self.initial_point['domain_id'] = domain_id

        elif self.selected_point_type == 'focal':
            domain_location_id = self.classify_point_per_domain_location(new_x_absolute, new_y_absolute)
            if domain_location_id is None:
                self.show_notification("Focal point cannot be placed on an axis.", bg_color='red')
                # Revert input fields to previous valid values
                x_prev, y_prev = self.focal_points[self.selected_focal_glass_id]['abs_space_coords'] # Revert to absolute
                self.point_x_var.set(f"{x_prev:.2f}")
                self.point_y_var.set(f"{y_prev:.2f}")
                return
             
            # Use the 'attached' classification for focal points (glass_point_id)
            glass_point_id_new_location = self.classify_point_per_domain_attached(new_x_absolute, new_y_absolute)
            if glass_point_id_new_location is None or glass_point_id_new_location != self.selected_focal_glass_id:
                self.show_notification(f"Focal point {self.selected_focal_glass_id} cannot be moved to a different 'attached' quadrant via direct input.", bg_color='red')
                # Revert input fields
                x_prev, y_prev = self.focal_points[self.selected_focal_glass_id]['abs_space_coords'] # Revert to absolute
                self.point_x_var.set(f"{x_prev:.2f}")
                self.point_y_var.set(f"{y_prev:.2f}")
                return

            # Update the focal point data
            point_data = self.focal_points[self.selected_focal_glass_id]
            point_data['abs_space_coords'] = np.array([new_x_absolute, new_y_absolute])
            point_data['rel_space_coords'] = np.array([new_x_relative, new_y_relative]) # Update relative too
            point_data['angle_theta'] = calculate_theta(new_x_relative, new_y_relative) # Use relative for angle calculation
            point_data['angle_delta'] = calculate_delta(new_x_relative, new_y_relative, domain_location_id) # Use relative for angle calculation
        
        self.setup_strvar.set("")
        self.compute_all_self_attributes()
        self.redraw_all_points_and_trajectories() # A full redraw is correct here as the point's position is definitively changed by input
        self.update_results_frame()
        self.update_point_input_fields() # Refresh fields with potentially rounded values and update outline
        self.show_notification("Coordinates applied.", bg_color='green')
        
    #%%Cosmetic functions
    def show_notification(self, message, bg_color='cyan', time=1500):
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(1)
        notification.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        tk.Label(notification, text=message, bg=bg_color, fg="black", padx=10, pady=5).pack()
        self.root.after(time, notification.destroy)  # Destroy the notification after 1.5 seconds
    
    def _show_message(self, message):
        """Helper to update the results label."""
        self.results_label.config(text=message)



#%%Main code to run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = Visualisation_app_straight(root)
    root.mainloop()