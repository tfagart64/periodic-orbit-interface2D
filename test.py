#%% Imports
import tkinter as tk
from periodic_orbit_interface2D.periodic_orbit_interface_straight import Visualisation_app_straight
from periodic_orbit_interface2D.periodic_orbit_interface_non_straight import Visualisation_app_non_straight

#%% Choose an app mode
mode = "straight"
mode = "non_straight"

#%%Main code to run the app
if __name__ == "__main__":
    root = tk.Tk()
    if mode == "straight":
        app = Visualisation_app_straight(root)
    elif mode == "non_straight":
        app = Visualisation_app_non_straight(root)
    root.mainloop()