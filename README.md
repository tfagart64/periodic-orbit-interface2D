# periodic-orbit-interface2D



This local application uses TKinter python module to create an interface. On this interface, the user can place focal points in a 2D phase space and observe the resulting limit cycle, should there be one. The app models only the behaviour expected in the case of a 2D piecewise affine system. The system should present only two threshold values for domain definitions, one for each component. This then divides the 2D space in 4 different domains. They will be named as follow : $1$ (top-right), $2$ (top-left), $3$ (bottom-left) and $4$ (bottom-right). The trajectory will alternate domains in the following order : $1 \to 2 \to 3 \to 4 \to 1$.

Two working "modes" of the application are available, one with equal degradation rates called "straight" mode and whose corresponding class is Visualisation_app_straight and the other with degradation rates depending on the component and the domain called "non_straight" mode and whose corresponding class is "Visualisation_app_non_straight.

## Installation

The application package can be installed from TestPyPI using pip installer by typing the command below in a Python environment. It is recommanded to do so in a separated Python environnement. To use the application, run the test files contained in the `tests` folder.

### Unix / macOS

```bash
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ periodic-orbit-interface2D
```

### Windows

```bash
py -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ periodic-orbit-interface2D
```

## Mathematical context of the application use

To be as general possible without introducing heavy notations, we use the form given in the equation below:

```math
    \frac{dx}{dt} = \kappa(x) - \Gamma(x)\, x
```

Here, $`\kappa : \mathbb{R}_{+}^{n} \to \mathbb{R}_{+}^{n}`$ is a vector of piecewise constant production rates, which can be expressed using step functions $\mathrm{s}^\pm(x_j,\theta_j)$. $\Gamma \in \mathbb{R}_{+}^{n\times n}$ is a diagonal matrix whose diagonal entries are degradation coefficients, which can also be expressed using the same step functions $\mathrm{s}^\pm(x_j,\theta_j)$. This correctly reflects the fact that the degradation coefficients depend both on the coordinate and on the domain.

Although it is still possible to further generalize the framework as in the original paper, we restrict ourselves here to the case where there exists a unique threshold $\theta_j$ per component. Moreover, we work in dimension $2$. We therefore have only two thresholds, $\theta_1$ and $\theta_2$, corresponding to the components $x_1$ and $x_2$, respectively. These two thresholds partition the space into four rectangular domains. We denote these domains by
- $a^1$ (upper right quadrant),
- $a^2$ (upper left quadrant),
- $a^3$ (lower left quadrant),
- $a^4$ (lower right quadrant).

For now, we assume that these domains do not include their boundary sets, or equivalently that they are equal to their own interiors. For instance, $a^1 = (\theta_1, +\infty) \times (\theta_2, +\infty)$.

Due to the piecewise affine nature of the equations, the system can be solved explicitly on each regular domain $a^i$. For each coordinate $j$, in each domain $i$, with initial condition $x^i \in a^i$ and for $t \ge 0$, we obtain:

```math
    \varphi^i_j(x^i,t) = x^i_j(t) = \frac{\kappa^i_j}{\gamma^i_j}
    + e^{-\gamma^i_j t} \left(x^i_j - \frac{\kappa^i_j}{\gamma^i_j} \right)
```

We further denote by $\phi^i = \phi(a^i)$ the focal point associated with the domain $a^i$, by $W^i$ the wall between the domains $a^i$ and $a^{i+1}$, and by $s_i$ the exit direction from the domain $a^i$. The expression of the focal point $\phi^i$ is given componentwise by:

```math
    \phi^i_j = \frac{\kappa^i_j}{\gamma^i_j}
```

We now impose the alternation of the domains as $1 \to 2 \to 3 \to 4 \to 1$. Without loss of generality, this assumption can always be made in dimension 2. Indeed, we assume that trajectories cannot cross a domain by passing through an intersection of walls, “diagonally”, or “through the center”. Moreover, the direction of rotation and the initial domain are merely conventions. Changing these conventions does not affect the nature of the analysis.

To enforce this domain alternation, we require suitable assumptions on the focal points. We assume that each focal point $\phi^i$ lies in the interior of the next domain $a^{i+1}$ (in particular, focal points cannot lie on the walls). Concretely, this is expressed by the following system of inequalities:

```math
    \left\{
    \begin{aligned}
        & \phi^1 \in a^2 & &\Longleftrightarrow & \phi^1_1 < \theta_1 \text{ and } \phi^1_2 > \theta_2\\
        & \phi^2 \in a^3 & &\Longleftrightarrow  &\phi^2_1 < \theta_1 \text{ and } \phi^2_2 < \theta_2\\
        & \phi^3 \in a^4 & &\Longleftrightarrow & \phi^3_1 > \theta_1 \text{ and } \phi^3_2 < \theta_2\\
        & \phi^4 \in a^1 & &\Longleftrightarrow & \phi^4_1 > \theta_1 \text{ and } \phi^4_2 > \theta_2
    \end{aligned}
    \right.
```
These assomptions allow us to have a minimal working system. They are sufficiently general to be applied to both application modes. For the mathematical part, the difference in the "straight" mode application is that all the two $\gamma$ coefficients are not using step functions in their expressions and are equal.

## Main differences between the arbitrary and equal degradation coefficients modes

As exposed in the introduction, there are two modes to use the application. These modes are the "straight" mode and the "non_straight" mode which correspond respectively to a system with all degradation rates equal and a system with degradation rates depending on the component and on the domain. They are called that way because having equal degradation rates makes straight trajectories in the phase space. In such a case, the study of the limit cycle existence and unicity is much simpler than in the general case. It was studied in a paper of Glass & Pasternak published in 1978 and named "Stable oscillations in mathematical models of biological control systems". They derive a criterion for the existence and unicity of a limit cycle in the case of equal degradation rates. Furthermore, and as trajectories in domains are straight lines segments, it is possible in this case to fully caracterise and compute the limit cycle return map, intersection points and trajectories. These additional computations and the more general degradation rates are the two main differences between the two modes of the application, which adapts to describe as fully as possible the two types of systems. 

## Application functionalities

The application presents different functionalities to customise your system and visualise the resulting behaviour. The application is mainly divided in four parts : the canvas, the tools panel, the entries panel and the results panel. The canvas is the interactive 2D space used to visualise your system behaviour. The tools panel is composed of different buttons allowing the user to either interact with the canvas, save the actual system setup or load other setups. The entry panels are used to enter precise parameter values. Finally, the result panel displays different computed properties of the system.

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

Finally, the "Dragging mode" drop-down menu allows the user to change the type of constraint applied to point dragging. Note that in any case, it is still not possible to drag a focal point out of the domain it belongs in. The shown value of this drop-down menu is the name of the actual mode applied. Base value will always be "Free". There are 5 types of possible dragging modes : "Free", "Horizontal", "Vertical", "Linear" and "Circular". The "Free" mode doesn't restrain the point drag in any direction. The "Horizontal" mode imposes a drag only in the horizontal direction (along the $x$ axis). The "Vertical" mode imposes a drag only in the vertical direction (along the $y$ axis). The "Linear " mode imposes a drag in the direction of the straight line linking the point and the center of rotation. Finally, the "Circular " mode imposes a drag along the circle whose center is the cernetr of rotation and whose radius is the distance from the center to the point. Note that dragging using this mode may not visually follow a real circular path, depending if the axis scales are the same or not.


### Entry panels

The entry panels are frames containing entry spaces. They are located in the middle and right parts of the application interface. They can be used to enter different parameter precise values in order to shape your system the way you want it to be. There are four different entry panels : the "Center coordinates" panel, the "Grid dimensions" panel, the "Point coordinates" panel and the "Gamma value (or values)" panel.

The "Center coordinates" panel can be used to enter the coordinates of the center of rotation of the system (the intersection of the two threshold axis). To modify these, just enter the new center coordinates in the fields and press the "Apply Center Coordinates" button or press the enter key. If one or more focal points have to be removed for the new center coordinates to be applied, a warning pop-up window will appear, naming the points to be removed and asking if the user wishes to continue. There also is a "Reset Center to (0,0)" button to reset the center coordinates to $(0,0)$ faster.

The "Grid dimensions" panel can be used to enter of the canvas boundaries. To modify these, just enter the new center boundaries in the fields and press the "Apply Dimensions" button or press the enter key.

The "Point Coordinates" panel can be used to modify the coordinates of the currently selected point. To do so, you should first select a point on the canvas by left-cliking on it. It will then appear with a blue outline around it. Selecting a point will unlock the entry fields inside the "Point coordinates" panel, and the point designation will appear in the panel (for example : "Focal point 3" or "Initial point"). Once the entry fields are unlocked, enter the new point coordinates and press the "Apply Point Coordinates" button or press the enter key to validate. Note that your request will be rejected if you're trying to place a focal point outside of its belonging domain.

The "Gamma value (or values)" panel can be used to modify the value or values of $\gamma$, depending on which application mode is used. If the application is used in "straight" mode, only one value is necessary for $\gamma$, as all degradation rates are equal. If the application is used in "non_straight" mode, eight different values of $\gamma$ can be entered (two different possible coordinates and four possible domains). When all entries are set, press the "Apply gamma value" button or the enter key to validate. Note that all $\gamma$ values should be strictly positive.


### Results panel

The results panel is text frame containing different computations and properties of the system studied. It is located in the right part of the application interface. It shows the coordinates of the points. If there are four focal points on the canvas, the results panel will also show the value of the criterion for a limit cycle called $\rho$ (see Glass & Pasternak, 1978, "Stable oscillations in mathematical models of biological control systems" for more details). Such a criterion can be computed for both application modes, even if its validity has not yet been attested for the "non_straight" mode. What is to be reminded is that should this criterion be strictly over $1$, a limit cycle should emerge in the system. If not, then no limit will appear.

If there is indeed a limit cycle, and the application mode "straight" is used, others features of this limit cycle are computed and shown in the results panel. They are the followings : the limit trajectory length and duration in each domain, the total length and duration of the limit trajectory, the amplitude of the limit cycle along both axis, the coordinates of the intersection points between the limit trajectory and the axis.
