# periodic-orbit-interface2D

This application uses TKinter python module to create an interface. On this interface, the user can place focal points in a 2D phase space and observe the resulting limit cycle, should there be one. The app models only the behaviour expected in the case of a 2D piecewise affine system. The system should present only two threshold values for domain definitions, one for each component. This then divides the 2D space in 4 different domains. They will be named as follow : $1$ (top-right), $2$ (top-left), $3$ (bottom-left) and $4$ (bottom-right). The trajectory will alternate domains in the following order : $1 \to 2 \to 3 \to 4 \to 1$. Two versions of the application are available, one with equal degradation rates called Visualisation_app_straight and the other with degradation rates depending on the component and the domain called Visualisation_app_non_straight.

## Precise mathematical context of the application use

## Application functionalities

The application presents different functionalities to customise your system and visualise the resulting behaviour. The application is mainly divided in four parts : the canvas, the tools panel, the entries panel and the results panel. The canvas is the interactive 2D space used to visualise your system behaviour. The tools panel is composed of different buttons allowing the user to either interact with the canvas, save the actual system setup or load other setups. The entries panel are used to enter precise parameter values. Finally, the result panel displays different computed properties of the system.

### Canvas panel

The canvas panel is the very core of this application. It is located at the left part of the application window. It consists of a 2D interactive space with a Cartesian coordinate system. This 2D space is divided in four domains by two thresholds (one horizontal and one vertical). Different colors are used to denote each domain.

To start visualising trajectories, simply place a focal point in each of the four domains. To add a focal point, left-click on the canvas in the domain you wish to add the focal point (it is not possible to place a focal point on one of the threshold's axis). You'll notice that its color is the same as a domain one's, but with shifted of a quadrant. In fact, each focal point has the color of the domain \textbf{from which it is the focal point}. For example, a trajectory in starting in the purple domain (domain 1, top-right) will go toward the purple focal point until it switches to the yellow domain (domain 2, top-left).

As you've added the four focal points, you should now add the initial point of your trajectory. You can do so by right-clicking anywhere on the canvas (except at the intersection of the thresholds). The initial point will appear in black.

When the initial point is added, a black trajectory starting from this point should appear on the canvas (if there are four focal points). The dotted lines represent the continuation of the partial trajectories if they effectively reached the focal points. If the app is used in the "straight" mode, the limit cycle trajectory should also appear in red, if the system allows the emergence of a limit cycle.

We've now seen the base use of the canvas functionalities. The canvas functionalities present further are not the main ones but allow users to manipulate as easily as possible the system.

Next tool is the ability to select a point when left-clicking on it (either a focal or initial point). This will circle the point with a blue outline, and will allow the user to check and modify its coordinates using the coordinates entry.

You can also drag a point (again, either focal or initial) by left-clicking on it and maintaining left-click while moving the point around. Every canvas feature, entry variable and system property modified during the dragging action is instantly updated when dragging the point. This allows you to see the immediate effects of the system continuous change on its properties. Different dragging modes can be chosen in the tools panel to constrain the dragging direction.

### Tools panel

The tools panel is a groupement of the different button type functionalities of the application. It is located at the top of the middle panel. The buttons composing it are described below.

The "Undo focal point" button allows the user to suppress the last added focal point from the canvas. Pressing it again will suppress the previous one, and so on until there are none left. When clicked with no remaining focal points on the canvas, a warning message should appear in yellow. Removing a focal point will always result in suppressing various elements needing four focal points to exists, such as the trajectory, the potential limit trajectory and the limit cycle criterion $\rho$.

The "Remove initial point" button will remove the initial point from the canvas. When clicked with no remaining initial point on the canvas, a warning message should appear in yellow. Removing the initial point will result in suppressing the trajectory, but not the limit one if it exists.

The "Clear points" button will remove all focal and initial points from the canvas. Clearing points will result in suppresing all points linked features.

For the good comprehension of two next tools use, a definition of a setup is given. A csv setup file is a file containing all parameters necessary to describe the studied system. These files are stored in a folder called the "setup folder". Note that this folder is different for the straight and non_straight modes of the application. The parameters stored in a csv setup file are the followings : the canvas grid dimensions, the center coordinates (intersection point of the two thresholds), the focal points coordinates (if the points exist), the initial point coordinates (if it exists) and the degradation coefficient(s) value(s), depending on which application mode is used.

The "Change setup storage folder" button allows the user to change the setup folder direction. Clicking it opens a Tkinter pop-up window asking you to choose a new setup storage folder. This pop-up window should also appear the first time the application, or if the defined storage folder is missing. This direction is then stored in Python configuration cache memory and will not need to be specified again, except if using the "Change setup storage folder" button, or if the defined storage file folder goes missing.

The "Save setup" button allows a user to save the actual system setup. It opens a Tkinter pop-up window asking the user to give the name of the setup, and then to validate it (which can be done by using the validate button or by pressing enter). The user can also cancel the operation. If the setup name is already used, another pop-up window is opened, asking the user if the new setup should replace the previous one, if it should be saved under the same name but with a suffixe or if the user wants to cancel the operation to come back to the previous pop-up window. Saving the setup will create a csv file at the format "setup_name.csv" in the setup folder.

The "Setup selection" tool is a interactive drop-down menu of the existing saved setup files. Its shown value is either nothing is the actual system setup has not been saved yet, or the name of the setup selected or most recently saved. Any parameter modification will result in this shown value being set to nothing. Setups can then be selected in this drop-down menu. Selecting a setup will apply it to the application, showing it on the canvas, along with relevant point linked constructions and properties. The "base" setup name holds a particular meaning in this context. It is a general setup with simple parameters values, which is used when starting the application for the first time. The setup save name "base" can also be used to modify the base setup appearing on screen when starting the application. To do so, just configure the base setup as you want it and save the setup under the name "base".

Finally, the "Dragging mode" drop-down menu allows the user to change the type of constraint applied to point dragging. Note that in any case, it is still not possible to drag a focal point out of the domain it belongs in. The shown value of this drop-down menu is the name of the actual mode applied. Base value will always be "Free". There are 5 types of possible dragging modes : "Free", "Horizontal", "Vertical", "Linear" and "Circular". The "Free" mode doesn't restrain the point drag in any direction. The "Horizontal" mode imposes a drag only in the horizontal direction (along the $x$ axis). The "Vertical" mode imposes a drag only in the vertical direction (along the $y$ axis). The "Linear " mode imposes a drag in the direction of the straight line linking the point and the center of rotation. Finally, the "Circular " mode imposes a drag along the circle whose center is the cernetr of rotation and whose radius is the distance from the center to the point. Note that that dragging using this mode may not follow a real circular, depending if the axis scales are the same or not.


### Entries panels

### Results panel

### Differences between the arbitrary and equal degradation coefficients versions
