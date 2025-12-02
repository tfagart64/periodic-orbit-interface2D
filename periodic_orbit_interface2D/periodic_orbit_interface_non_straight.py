#%%Importations
import tkinter as tk
from tkinter import ttk  # Using ttk for potentially more modern widgets
import numpy as np
import pandas as pd
from .utilitary import switch_axis
from .base_template_app import Visualisation_app_template

#%% Visualisation_app_non_straight class
class Visualisation_app_non_straight(Visualisation_app_template):
    
    def __init__(self, root):
        super().__init__(root)
    
    def _get_app_mode(self):
        self.app_mode = "non_straight"
    
    #%% Rho function
    @property
    def _rho(self):
        if len(self.focal_points) != 4:
            return float('nan')
        try:
            phi_11, phi_12 = self.focal_points[1]['rel_space_coords']
            phi_21, phi_22 = self.focal_points[2]['rel_space_coords']
            phi_31, phi_32 = self.focal_points[3]['rel_space_coords']
            phi_41, phi_42 = self.focal_points[4]['rel_space_coords']
            
            gamma_11, gamma_12 = self.gamma_array[:,0]
            gamma_21, gamma_22 = self.gamma_array[:,1]
            gamma_31, gamma_32 = self.gamma_array[:,2]
            gamma_41, gamma_42 = self.gamma_array[:,3]
            
            T1 = (gamma_12*np.abs(phi_12)) / (gamma_11*np.abs(phi_11))
            T2 = (gamma_21*np.abs(phi_21)) / (gamma_22*np.abs(phi_22))
            T3 = (gamma_32*np.abs(phi_32)) / (gamma_31*np.abs(phi_31))
            T4 = (gamma_41*np.abs(phi_41)) / (gamma_42*np.abs(phi_42))
            
            return T4*T3*T2*T1
        except Exception:
            return float('nan')
    
    #%% Setup handling functions
    def _get_base_dataframe_setup(self):
        data = {
            "min_x": -5., "max_x": 5.,
            "min_y": -5., "max_y": 5,
            "center_x": 0., "center_y": 0.,
            "focal1_x": -1., "focal1_y": 3.,
            "focal2_x": -2, "focal2_y": -1,
            "focal3_x": 2, "focal3_y": -4,
            "focal4_x": 3, "focal4_y": 2,
            "init_x": 4., "init_y": 3.5,
            "gamma_11": 1, "gamma_12": 2,
            "gamma_21": 3, "gamma_22": 4,
            "gamma_31": 3, "gamma_32": 2,
            "gamma_41": 1, "gamma_42": 4,
        }
        
        df = pd.DataFrame([data])
        
        return df
    
    def _format_to_csv_savable(self):
        # --- Retrieving grid dimensions ---
        grid_dim_array = np.array([[self.min_space_x, self.max_space_x],
                                   [self.min_space_y, self.max_space_y]])
        min_x, max_x = grid_dim_array[0]
        min_y, max_y = grid_dim_array[1]
    
        # --- Retrieving center data ---
        center_x, center_y = self.center_coords
    
        # --- Retrieving focal points data ---
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
    
        # --- Retrieving initial point ---
        if not self.initial_point:
            init_x, init_y = None, None
        else:
            init_x, init_y = self.initial_point['abs_space_coords']
        
        # --- Retrieving gamma data ---
        gamma_data = self.gamma_array
        
        # --- Store data in a data frame ---
        data = {
            "min_x": min_x, "max_x": max_x,
            "min_y": min_y, "max_y": max_y,
            "center_x": center_x, "center_y": center_y,
            "focal1_x": focals[0], "focal1_y": focals[1],
            "focal2_x": focals[2], "focal2_y": focals[3],
            "focal3_x": focals[4], "focal3_y": focals[5],
            "focal4_x": focals[6], "focal4_y": focals[7],
            "init_x": init_x, "init_y": init_y,
            "gamma_11": gamma_data[0,0], "gamma_12": gamma_data[1,0],
            "gamma_21": gamma_data[0,1], "gamma_22": gamma_data[1,1],
            "gamma_31": gamma_data[0,2], "gamma_32": gamma_data[1,2],
            "gamma_41": gamma_data[0,3], "gamma_42": gamma_data[1,3],
        }
        
        df = pd.DataFrame([data])
        
        return(df)
    
    def _modify_variables_from_setup_dataframe(self, setup_dataframe):
        """
        Modify (or create) the object variables from a setup dataframe.
        """
        # Extract the row from the dataframe (only one expected)
        row = setup_dataframe.iloc[0]
    
        # --- Update grid dimensions ---
        self.min_space_x = row["min_x"]
        self.max_space_x = row["max_x"]
        self.min_space_y = row["min_y"]
        self.max_space_y = row["max_y"]
        
        # --- Update center coordinates ---
        self.center_coords = np.array([row["center_x"], row["center_y"]])
    
        # --- Update focal points ---
        self.focal_points = {}
        for i in range(4):
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
        
        # --- Update gamma values ---
        try:
            self.gamma_array = np.array([[row["gamma_11"], row["gamma_21"], row["gamma_31"], row["gamma_41"]],
                                         [row["gamma_12"], row["gamma_22"], row["gamma_32"], row["gamma_42"]]])
        except KeyError:
            print('gamma values were not found, keeping the same values')
    
    def _update_gamma_input_fields(self):
        self.gamma_11_var.set(f"{self.gamma_array[0,0]:.2f}")
        self.gamma_12_var.set(f"{self.gamma_array[1,0]:.2f}")
        self.gamma_21_var.set(f"{self.gamma_array[0,1]:.2f}")
        self.gamma_22_var.set(f"{self.gamma_array[1,1]:.2f}")
        self.gamma_31_var.set(f"{self.gamma_array[0,2]:.2f}")
        self.gamma_32_var.set(f"{self.gamma_array[1,2]:.2f}")
        self.gamma_41_var.set(f"{self.gamma_array[0,3]:.2f}")
        self.gamma_42_var.set(f"{self.gamma_array[1,3]:.2f}")
    
    #%% Update canvas functions
    def _update_all_canvas_focal_point_linked_constructions(self):
        self._update_canvas_normal_traj()
    

    def _update_canvas_normal_traj(self, nb_iter=50, with_dashed_line=True):
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
                    intersect_point = self._draw_curved_line_with_axis_cut(point1_traj, point2_traj, axis, self.canvas_norm_line_ids, line_color=self.color_norm_lines, line_width=self.line_width_norm, with_dashed_line=with_dashed_line)
                    
                    # Update variables for the next iteration
                    glass_point_id = glass_point_id % 4 + 1 # Cycle through focal points (1->2, 2->3, 3->4, 4->1)
                    point1_traj, point2_traj = intersect_point, self.focal_points[glass_point_id]['rel_space_coords'] 
                    axis = switch_axis(axis) # Alternate axis (x=0 -> y=0, y=0 -> x=0)
            except Exception as e:
                self._show_notification(f"Error drawing normal trajectory: {e}", bg_color='red')
    
    def _compute_curve_coords_tab(self, x1_init_point, x2_init_point, x1_focal_point, x2_focal_point, mode='rel'):
        """
        Compute the coords of the exponential curved trajectory between two points.
        Works either with absolute or relative coords.
        """
        t_start_exponent = -3
        t_end_exponent = 3
        nb_points = 1000
        t_array = np.logspace(t_start_exponent, t_end_exponent, nb_points-2)
        
        if mode == 'rel':
            start_domain_id = self._classify_point_per_domain_location(x1_init_point + self.center_coords[0], x2_init_point + self.center_coords[1], is_focal_point=False)
        elif mode == 'abs':
            start_domain_id = self._classify_point_per_domain_location(x1_init_point, x2_init_point, is_focal_point=False)
        else:
            raise ValueError(f"Invalid mode name: '{mode}'. Expected 'rel' or 'abs'.")
        
        x1_array = x1_focal_point + (x1_init_point - x1_focal_point) * np.exp(-self.gamma_array[0][start_domain_id-1] * t_array)
        x2_array = x2_focal_point + (x2_init_point - x2_focal_point) * np.exp(-self.gamma_array[1][start_domain_id-1] * t_array)
        
        # Add initial and last points
        x1_array = np.array([x1_init_point] + list(x1_array) + [x1_focal_point])
        x2_array = np.array([x2_init_point] + list(x2_array) + [x2_focal_point])
        
        return(np.transpose(np.array([x1_array, x2_array])))

    def _find_intersection_point_between_curve_and_axis(self, curved_traj_array_relative, axis):
        """
        Trouve le point d'intersection entre une trajectoire 2D et un axe spécifié.
        
        Paramètres
        ----------
        curved_traj_array_relative : array-like de forme (N, 2)
            Tableau contenant les points de la trajectoire [x, y].
        axis : str
            'x=0' ou 'y=0' selon l'axe recherché.
            
        Retour
        ------
        (x, y) : tuple ou None
            Coordonnées du point d'intersection (interpolé), ou None si pas d'intersection.
        """
    
        traj = np.array(curved_traj_array_relative)
        x_vals = traj[:, 0]
        y_vals = traj[:, 1]
    
        if axis == 'x=0':
            values = x_vals
            other = y_vals
        elif axis == 'y=0':
            values = y_vals
            other = x_vals
        else:
            raise ValueError(f"Invalid axis name: '{axis}'. Expected 'x=0' or 'y=0'.")
    
        # On cherche un changement de signe dans la valeur correspondant à l'axe
        sign_changes = np.where(np.sign(values[:-1]) * np.sign(values[1:]) < 0)[0]
    
        if len(sign_changes) == 0:
            return None  # Pas d'intersection détectée
    
        # On suppose une seule intersection (ou on prend la première)
        last_index = sign_changes[0]
    
        # Interpolation linéaire pour estimer le point exact
        v1, v2 = values[last_index], values[last_index+1]
        o1, o2 = other[last_index], other[last_index+1]
        t = abs(v1) / (abs(v2 - v1))  # fraction entre les deux points
    
        if axis == 'x=0':
            x = 0
            y = o1 + t * (o2 - o1)
        else:  # y=0
            y = 0
            x = o1 + t * (o2 - o1)
    
        return (np.array([x, y]), last_index)

        
    def _draw_curved_line_with_axis_cut(self, init_point_rel, focal_point_rel, axis, storage_canvas_id_list, line_color="black", line_width=2, with_dashed_line=True):
        """
        Draws a line between two points (in space coordinates relative to the center) and handles axis crossing.
        Returns the intersection point in space coordinates relative to the center.
        Includes robust checks for axis crossing.
        """
        x_init_rel, y_init_rel = init_point_rel
        x_focal_rel, y_focal_rel = focal_point_rel
        
        curved_traj_array_relative = self._compute_curve_coords_tab(x_init_rel, y_init_rel, x_focal_rel, y_focal_rel)
        
        intersect_point_rel, last_index = self._find_intersection_point_between_curve_and_axis(curved_traj_array_relative, axis)
        
        # Extracting both parts of the trajectory
        curved_traj_array_relative_part1 = curved_traj_array_relative[:last_index+2, :]
        curved_traj_array_relative_part2 = curved_traj_array_relative[last_index:, :]
        curved_traj_array_relative_part1[last_index+1,:] = intersect_point_rel
        curved_traj_array_relative_part2[0,:] = intersect_point_rel
        
        # Convert relative coordinates to absolute coordinates for drawing on canvas
        curved_traj_array_abs_part1 = curved_traj_array_relative_part1 + self.center_coords
        curved_traj_array_abs_part2 = curved_traj_array_relative_part2 + self.center_coords
        
        # Extract to make an acceptable entry for canvas transform
        x_curved_traj_array_abs_part1 = curved_traj_array_abs_part1[:,0]
        y_curved_traj_array_abs_part1 = curved_traj_array_abs_part1[:,1]
        x_curved_traj_array_abs_part2 = curved_traj_array_abs_part2[:,0]
        y_curved_traj_array_abs_part2 = curved_traj_array_abs_part2[:,1]
        
        # Transform to canvas coordinates
        x_curved_traj_array_canvas_part1, y_curved_traj_array_canvas_part1 = self._get_canvas_coords_from_absolute_space_coords(x_curved_traj_array_abs_part1, y_curved_traj_array_abs_part1)
        x_curved_traj_array_canvas_part2, y_curved_traj_array_canvas_part2 = self._get_canvas_coords_from_absolute_space_coords(x_curved_traj_array_abs_part2, y_curved_traj_array_abs_part2)
        
        # Fuse back arrays
        curved_traj_array_canvas_part1 = np.transpose(np.array([x_curved_traj_array_canvas_part1, y_curved_traj_array_canvas_part1]))
        curved_traj_array_canvas_part2 = np.transpose(np.array([x_curved_traj_array_canvas_part2, y_curved_traj_array_canvas_part2]))
        
        # Reshape to make acceptable entry for create line
        size1 = curved_traj_array_canvas_part1.shape[0]
        size2 = curved_traj_array_canvas_part2.shape[0]
        array_create_line_part1 = np.reshape(curved_traj_array_canvas_part1, (1,2*size1))[0,:]
        array_create_line_part2 = np.reshape(curved_traj_array_canvas_part2, (1,2*size2))[0,:]
        
        # Draw the 1st part (before the axis) as continuous
        canvas_line_id = self.canvas.create_line(list(array_create_line_part1), fill=line_color, width=line_width)
        
        
        storage_canvas_id_list.append(canvas_line_id)
        
        if with_dashed_line:
            # Draw the 2nd part (after the axis) as dashed
            canvas_line_id = self.canvas.create_line(list(array_create_line_part2), fill=line_color, width=line_width, dash=(4, 8))
            storage_canvas_id_list.append(canvas_line_id)
        
        return intersect_point_rel # Return the intersection point in relative coordinates
    
    #%% Functions to handle the gamma input frame
    def _create_gamma_input_frame(self):
        """Creates a dedicated section in the right panel for gamma input fields."""
        self.gamma_input_frame = ttk.LabelFrame(self.right_frame, text="Gamma values", padding=10)
        self.gamma_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Domaine 1 input frame
        self.D1_input_frame = ttk.LabelFrame(self.gamma_input_frame, padding=5, text="Domain 1 (Top-right)")
        self.D1_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.gamma_11_var = tk.StringVar(value=f"{self.gamma_array[0,0]:.2f}")
        self.gamma_11_entry = ttk.Entry(self.D1_input_frame, textvariable=self.gamma_11_var, width=10)
        self.gamma_11_entry.pack(side="left", padx=5)
        
        self.gamma_12_var = tk.StringVar(value=f"{self.gamma_array[1,0]:.2f}")
        self.gamma_12_entry = ttk.Entry(self.D1_input_frame, textvariable=self.gamma_12_var, width=10)
        self.gamma_12_entry.pack(side="left", padx=5)
        
        # Domaine 2 input frame
        self.D2_input_frame = ttk.LabelFrame(self.gamma_input_frame, padding=5, text="Domain 2 (Top-left)")
        self.D2_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.gamma_21_var = tk.StringVar(value=f"{self.gamma_array[0,1]:.2f}")
        self.gamma_21_entry = ttk.Entry(self.D2_input_frame, textvariable=self.gamma_21_var, width=10)
        self.gamma_21_entry.pack(side="left", padx=5)
        
        self.gamma_22_var = tk.StringVar(value=f"{self.gamma_array[1,1]:.2f}")
        self.gamma_22_entry = ttk.Entry(self.D2_input_frame, textvariable=self.gamma_22_var, width=10)
        self.gamma_22_entry.pack(side="left", padx=5)
        
        # Domaine 3 input frame
        self.D3_input_frame = ttk.LabelFrame(self.gamma_input_frame, padding=5, text="Domain 3 (Bottom-left)")
        self.D3_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.gamma_31_var = tk.StringVar(value=f"{self.gamma_array[0,2]:.2f}")
        self.gamma_31_entry = ttk.Entry(self.D3_input_frame, textvariable=self.gamma_31_var, width=10)
        self.gamma_31_entry.pack(side="left", padx=5)
        
        self.gamma_32_var = tk.StringVar(value=f"{self.gamma_array[1,2]:.2f}")
        self.gamma_32_entry = ttk.Entry(self.D3_input_frame, textvariable=self.gamma_32_var, width=10)
        self.gamma_32_entry.pack(side="left", padx=5)
        
        # Domaine 4 input frame
        self.D4_input_frame = ttk.LabelFrame(self.gamma_input_frame, padding=5, text="Domain 4 (Bottom-right)")
        self.D4_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.gamma_41_var = tk.StringVar(value=f"{self.gamma_array[0,3]:.2f}")
        self.gamma_41_entry = ttk.Entry(self.D4_input_frame, textvariable=self.gamma_41_var, width=10)
        self.gamma_41_entry.pack(side="left", padx=5)
        
        self.gamma_42_var = tk.StringVar(value=f"{self.gamma_array[1,3]:.2f}")
        self.gamma_42_entry = ttk.Entry(self.D4_input_frame, textvariable=self.gamma_42_var, width=10)
        self.gamma_42_entry.pack(side="left", padx=5)
        
        self.apply_gamma_button = ttk.Button(self.gamma_input_frame, text="Apply gamma values", command=self._apply_gamma_values)
        self.apply_gamma_button.pack(fill=tk.X, pady=5)
        self.apply_gamma_button.pack(fill=tk.X, pady=5)
        
        # Register this frame
        self._register_return_binding(self.gamma_input_frame, self._apply_gamma_values)
    
    def _apply_gamma_values(self):
        """
        Applies the coordinates entered in the input fields to the currently selected point.
        Performs validation and updates the canvas and calculations.
        Input coordinates are now absolute instead of relative.
        """
        try:
            new_gamma_11 = float(self.gamma_11_var.get())
            new_gamma_12 = float(self.gamma_12_var.get())
            new_gamma_21 = float(self.gamma_21_var.get())
            new_gamma_22 = float(self.gamma_22_var.get())
            new_gamma_31 = float(self.gamma_31_var.get())
            new_gamma_32 = float(self.gamma_32_var.get())
            new_gamma_41 = float(self.gamma_41_var.get())
            new_gamma_42 = float(self.gamma_42_var.get())
        except ValueError:
            self._show_notification("Invalid value. Please enter all gamma values.", bg_color='orange')
            return
        
        # Change gamma value
        self.gamma_array = np.array([[new_gamma_11, new_gamma_21, new_gamma_31, new_gamma_41],
                                     [new_gamma_12, new_gamma_22, new_gamma_32, new_gamma_42]])
        
        # Update the rest of the app
        self.setup_strvar.set("")
        self._update_all_canvas_focal_point_linked_constructions()
        self._update_result_frame()
        self._show_notification("Gamma values applied.", bg_color='green')
    
    #%% Update result frame
    def _update_result_frame(self):
        pass
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
                results_text += f"rho : {self._rho:.4f}\n"
                if self._rho > 1:
                    results_text += "\n Apparition d'une orbite périodique \n"
                else:
                    results_text += "\n Pas d'orbite périodique \n"
            
        self.results_label.config(text=results_text)