#%% Imports
import tkinter as tk
from periodic_orbit_interface2D.periodic_orbit_interface_non_straight import Visualisation_app_non_straight

#%%Main code to run the app in the "non_straight" mode
if __name__ == "__main__":
    root = tk.Tk()
    app = Visualisation_app_non_straight(root)
    root.mainloop()