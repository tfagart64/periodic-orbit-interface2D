#%%Importations
import tkinter as tk
from tkinter import ttk  # Using ttk for potentially more modern widgets
import numpy as np
import pandas as pd
from utilitary import switch_axis
from base_template_app import Visualisation_app_template

#%% Visualisation_app_straight class
class Visualisation_app_straight(Visualisation_app_template):
    # def __init__(self, root):
    #     super().__init__(root)
    
    def _get_app_mode(self):
        self.app_mode = "straight"
    
    #%%Calculus linked functions
    # Ces fonctions opèrent sur les space_coords qui sont maintenant relatives au centre
    @property
    def _rho(self):
        if len(self.focal_points) != 4:
            return float('nan')
        try:
            a1, b1 = self.focal_points[1]['rel_space_coords'] 
            a2, b2 = self.focal_points[2]['rel_space_coords'] 
            a3, b3 = self.focal_points[3]['rel_space_coords'] 
            a4, b4 = self.focal_points[4]['rel_space_coords']
            return a4*b3*a2*b1 / (b4*a3*b2*a1)
        except Exception:
            return float('nan')
    
    @property
    def _r(self):
        if len(self.focal_points) != 4:
            return float('nan')
        try:
            a1, b1 = self.focal_points[1]['rel_space_coords'] 
            a2, b2 = self.focal_points[2]['rel_space_coords'] 
            a3, b3 = self.focal_points[3]['rel_space_coords'] 
            a4, b4 = self.focal_points[4]['rel_space_coords']
            return -1/a1 + b1/(a1*b2) - b1*a2/(a1*b2*a3) + b1*a2*b3/(a1*b2*a3*b4)
        except Exception:
            return float('nan')
    
    @property
    def _h1_lim(self):
        if self._rho <= 1:
            return 0
        return (self._rho - 1) / self._r
    
    def _compute_lim_trajs_lengths_per_zones(self):
        dist1 = np.linalg.norm(self.intersect_point1 - self.start_limit_point)
        dist2 = np.linalg.norm(self.intersect_point2 - self.intersect_point1)
        dist3 = np.linalg.norm(self.intersect_point3 - self.intersect_point2)
        dist4 = np.linalg.norm(self.start_limit_point - self.intersect_point3)
        
        dist_total = dist1 + dist2 + dist3 + dist4
        
        return(dist1, dist2, dist3, dist4, dist_total)
        
    def _compute_lim_trajs_durations_per_zones(self):
        time1 = np.log((self.start_limit_point[0] - self.focal_points[1]['rel_space_coords'][0]) / (self.intersect_point1[0] - self.focal_points[1]['rel_space_coords'][0])) * 1 / self.gamma
        time2 = np.log((self.intersect_point1[0] - self.focal_points[2]['rel_space_coords'][0]) / (self.intersect_point2[0] - self.focal_points[2]['rel_space_coords'][0])) * 1 / self.gamma
        time3 = np.log((self.intersect_point2[0] - self.focal_points[3]['rel_space_coords'][0]) / (self.intersect_point3[0] - self.focal_points[3]['rel_space_coords'][0])) * 1 / self.gamma
        time4 = np.log((self.intersect_point3[0] - self.focal_points[4]['rel_space_coords'][0]) / (self.start_limit_point[0] - self.focal_points[4]['rel_space_coords'][0])) * 1 / self.gamma
        
        time_total = time1 + time2 + time3 + time4
        
        return(time1, time2, time3, time4, time_total)
    
    def _compute_lim_trajs_amplitudes(self):
        amp_x = np.linalg.norm(self.intersect_point2 - self.start_limit_point)
        amp_y = np.linalg.norm(self.intersect_point3 - self.intersect_point1)
        
        return(amp_x, amp_y)
    
    #%% Setup handling function
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
            "gamma": 1,
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
        gamma = self.gamma
        
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
            "gamma": gamma,
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
        
        # --- Update gamma value ---
        try:
            self.gamma = row["gamma"]
        except KeyError:
            print('Valeur de gamma non trouvée (reste inchangée)')
    
    def _update_gamma_input_fields(self):
        self.gamma_var.set(f"{self.gamma:.2f}")
    
    #%% Update canvas functions
    def _update_all_canvas_focal_point_linked_constructions(self):
        self._update_canvas_limit_traj()
        self._update_canvas_normal_traj()
    
    def _update_canvas_limit_traj(self, with_dashed_line=False):
        """
        Draws the limit trajectory (if a periodic orbit exists).
        Clears previous limit trajectories before redrawing.
        """
        # Clear all limit trajectories
        for canvas_line_id in self.canvas_lim_line_ids:
            self.canvas.delete(canvas_line_id)
        self.canvas_lim_line_ids = []
        
        # Only draw if 4 focal points exist and rho indicates a periodic orbit (and rho is a valid number)
        if len(self.focal_points) == 4 and self._rho > 1 and not np.isnan(self._rho) and not np.isinf(self._rho):
            try:
                # start_limit_point is now relative to center
                self.start_limit_point = np.array([self._h1_lim, 0]) 
                
                # Traj 1 (from h1_lim to focal point 1, crossing x=0)
                point1_traj1, point2_traj1 = self.start_limit_point, self.focal_points[1]['rel_space_coords']
                self.intersect_point1 = self._draw_line_with_axis_cut(point1_traj1, point2_traj1, 'x=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Traj 2 (from intersect_point1 to focal point 2, crossing y=0)
                point1_traj2, point2_traj2 = self.intersect_point1, self.focal_points[2]['rel_space_coords']
                self.intersect_point2 = self._draw_line_with_axis_cut(point1_traj2, point2_traj2, 'y=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Traj 3 (from intersect_point2 to focal point 3, crossing x=0)
                point1_traj3, point2_traj3 = self.intersect_point2, self.focal_points[3]['rel_space_coords']
                self.intersect_point3 = self._draw_line_with_axis_cut(point1_traj3, point2_traj3, 'x=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Traj 4 (from intersect_point3 to focal point 4, crossing y=0)
                point1_traj4, point2_traj4 = self.intersect_point3, self.focal_points[4]['rel_space_coords']
                intersect_point4 = self._draw_line_with_axis_cut(point1_traj4, point2_traj4, 'y=0', self.canvas_lim_line_ids, line_color=self.color_lim_lines, line_width=self.line_width_lim, with_dashed_line=with_dashed_line)
                
                # Check if the trajectory closes back to the start_limit_point (with a small tolerance)
                if np.linalg.norm(self.start_limit_point - intersect_point4) >= 1e-8: # Increased tolerance slightly for floating point arithmetic
                    self._show_notification('Problem in calculation or low precision for limit trajectory closing.', bg_color='orange')
            except Exception as e:
                self._show_notification(f"Error drawing limit trajectory: {e}", bg_color='red')

    def _update_canvas_normal_traj(self, nb_iter=20, with_dashed_line=True):
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
                    intersect_point = self._draw_line_with_axis_cut(point1_traj, point2_traj, axis, self.canvas_norm_line_ids, line_color=self.color_norm_lines, line_width=self.line_width_norm, with_dashed_line=with_dashed_line)
                    
                    # Update variables for the next iteration
                    glass_point_id = glass_point_id % 4 + 1 # Cycle through focal points (1->2, 2->3, 3->4, 4->1)
                    point1_traj, point2_traj = intersect_point, self.focal_points[glass_point_id]['rel_space_coords'] 
                    axis = switch_axis(axis) # Alternate axis (x=0 -> y=0, y=0 -> x=0)
            except Exception as e:
                self._show_notification(f"Error drawing normal trajectory: {e}", bg_color='red')
    
    
    #%% Functions to handle the gamma input frame
    def _create_gamma_input_frame(self):
        """Creates a dedicated section in the right panel for gamma input fields."""
        self.gamma_input_frame = ttk.LabelFrame(self.right_frame, text="Gamma value", padding=10)
        self.gamma_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.gamma_input_frame, text="Gamma value:").pack(pady=2)
        self.gamma_var = tk.StringVar(value=f"{self.gamma:.2f}")
        self.gamma_entry = ttk.Entry(self.gamma_input_frame, textvariable=self.gamma_var)
        self.gamma_entry.pack(fill=tk.X, pady=2)
        
        self.apply_gamma_button = ttk.Button(self.gamma_input_frame, text="Apply gamma value", command=self._apply_gamma_value)
        self.apply_gamma_button.pack(fill=tk.X, pady=5)
        self.apply_gamma_button.pack(fill=tk.X, pady=5)
        
        # Register this frame
        self._register_return_binding(self.gamma_input_frame, self._apply_gamma_value)
    
    def _apply_gamma_value(self):
        """
        Applies the coordinates entered in the input fields to the currently selected point.
        Performs validation and updates the canvas and calculations.
        Input coordinates are now absolute instead of relative.
        """
        try:
            new_gamma = float(self.gamma_var.get()) # Read as absolute
        except ValueError:
            self._show_notification("Invalid value. Please enter gamma value.", bg_color='orange')
            return
        
        # Change gamma value
        self.gamma = new_gamma
        
        # Update the rest of the app
        self.setup_strvar.set("")
        self._update_result_frame()
        self._show_notification("Gamma value applied.", bg_color='green')
        
        
    #%% Update result frame function
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
                results_text += f"r : {self._r:.4f}\n"
                h1_lim_abs = self._h1_lim + self.center_coords[0]
                results_text += f"h1_lim : {h1_lim_abs:.4f}\n"
                
                if self._rho > 1 and not np.isnan(self._rho) and not np.isinf(self._rho): # Check for valid rho
                    results_text += "\n\nCaractéristiques de l'orbite périodique\n"
                    try:
                        dist1, dist2, dist3, dist4, dist_total = self._compute_lim_trajs_lengths_per_zones()
                        time1, time2, time3, time4, time_total = self._compute_lim_trajs_durations_per_zones()
                        amp_x, amp_y = self._compute_lim_trajs_amplitudes()
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
    

#%%Main code to run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = Visualisation_app_straight(root)
    root.mainloop()